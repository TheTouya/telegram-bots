import os
import random
import telebot
import time
import re
from telebot.util import quick_markup
from telebot.types import Message
from dotenv import load_dotenv
from typing import List, Dict
import json
from functools import wraps
load_dotenv()
api_key = os.getenv('TEST_KEY')
bot = telebot.TeleBot(api_key, parse_mode=None)

ADMIN_ID = os.getenv('ADMIN_ID')
ADMIN_PANEL_PASSWORD = os.getenv('ADMIN_PANEL_PASSWORD')
DATASET_FILE = "users.json"
LEGACY_BLOCKED_USERS = {1717677479}
dsbm_files_id = os.getenv("DSBM_FILE_IDS")
jazz_files_id=os.getenv("JAZZ_FILE_IDS")
data_base_channel = os.getenv("DATA_BASE_CHANNEL")
daily_channel = os.getenv("THETOUYAS")
jazz_list = [x.strip() for x in jazz_files_id.split(",") if x.strip()]
audio_list_dsbm = [x.strip() for x in dsbm_files_id.split(",") if x.strip()]
the_time = time.time()
blocked_users = set(LEGACY_BLOCKED_USERS)
banned_users = []
user_stat = {}
admin_stat = {}


def _getting_dataset() -> Dict:
    """Load the users dataset. A missing/corrupt file is treated as an empty dataset."""
    try:
        with open(DATASET_FILE, "r", encoding="utf-8") as file:
            dataset = json.load(file)
            if not isinstance(dataset, dict):
                raise ValueError("Dataset root must be a JSON object.")
            return dataset
    except FileNotFoundError:
        return {}
    except Exception as e:
        bot.send_message(ADMIN_ID, f"There was an error loading the dataset: {e}")
        return {}


def _save_dataset(dataset: Dict) -> None:
    """Persist the dataset."""
    temp_file = f"{DATASET_FILE}.tmp"
    try:
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(dataset, f, indent=4, ensure_ascii=False)
        os.replace(temp_file, DATASET_FILE)
    except Exception:
        try:
            if os.path.exists(temp_file):
                os.remove(temp_file)
        finally:
            raise


def _is_admin(user_id) -> bool:
    return str(user_id) == str(ADMIN_ID)


def _member_status_is_active(status: str) -> bool:
    return status in {"member", "administrator", "creator"}


def _get_membership(user_id: str) -> bool:
    """Check membership without crashing the whole handler if Telegram rejects the request."""
    try:
        member = bot.get_chat_member(daily_channel, int(user_id))
        return _member_status_is_active(member.status)
    except Exception as e:
        bot.send_message(ADMIN_ID, f"Could not check channel membership for {user_id}: {e}")
        return False


def processing_new_user(user_id: str) -> None:
    """Create a user record using the schema supplied by the bot owner."""
    dataset = _getting_dataset()
    if user_id in dataset:
        return

    try:
        user = bot.get_chat(int(user_id))
        is_member = _get_membership(user_id)

        birthdate = None
        if getattr(user, "birthdate", None):
            date = user.birthdate
            birthdate = {}
            if getattr(date, "day", None):
                birthdate["day"] = str(date.day)
            if getattr(date, "month", None):
                birthdate["month"] = str(date.month)
            if getattr(date, "year", None):
                birthdate["year"] = str(date.year)

        dataset[user_id] = {
            "name": user.first_name or "",
            "is_member": is_member,
            "is_blocked": False,
            "username": user.username,
            "birthday": birthdate,
            "bio": user.bio,
        }
        _save_dataset(dataset)
    except Exception as e:
        bot.send_message(ADMIN_ID, f"Error while adding user {user_id} to dataset: {e}")


def ensure_user(user_id: str) -> Dict:
    """Ensure the requested user exists and return their record."""
    user_id = str(user_id)
    dataset = _getting_dataset()

    if user_id not in dataset:
        bot.send_message(data_base_channel, f"A new user has started the bot {users_id}")
        processing_new_user(user_id)
        dataset = _getting_dataset()

    if user_id not in dataset:
        # This should only happen if Telegram/API access failed.
        return {}

    return dataset[user_id]


def update_user_membership(user_id: str, is_member: bool) -> None:
    dataset = _getting_dataset()
    user_id = str(user_id)
    if user_id in dataset:
        dataset[user_id]["is_member"] = bool(is_member)
        _save_dataset(dataset)


def is_user_blocked(user_id: str) -> bool:
    """Return the persisted block state from users.json."""
    record = ensure_user(str(user_id))
    return bool(record.get("is_blocked", False))


def set_user_blocked(user_id: str, blocked: bool) -> bool:
    """Persist a user's block state. Returns False if the user does not exist."""
    user_id = str(user_id)
    dataset = _getting_dataset()
    if user_id not in dataset:
        return False
    dataset[user_id]["is_blocked"] = bool(blocked)
    _save_dataset(dataset)

    if blocked:
        blocked_users.add(int(user_id))
    else:
        blocked_users.discard(int(user_id))
    return True


def access_denied(user_id: int) -> None:
    """Tell a blocked user that the bot is unavailable to them."""
    bot.send_message(
        user_id,
        "Sadly, you are blocked from using the bot :("
    )


def user_access_required(func):
    """Block all normal bot functionality for users marked is_blocked=true."""
    @wraps(func)
    def wrapper(message, *args, **kwargs):
        user_id = str(message.from_user.id)
        if not _is_admin(user_id):
            ensure_user(user_id)
            if is_user_blocked(user_id):
                access_denied(message.from_user.id)
                return
        return func(message, *args, **kwargs)
    return wrapper


def callback_access_required(func):
    """Same access check for callback queries."""
    @wraps(func)
    def wrapper(call, *args, **kwargs):
        user_id = str(call.from_user.id)
        if not _is_admin(user_id):
            ensure_user(user_id)
            if is_user_blocked(user_id):
                bot.answer_callback_query(
                    call.id,
                    "You are blocked from using this bot.",
                    show_alert=True
                )
                return
        return func(call, *args, **kwargs)
    return wrapper


# Keep old in-memory state synchronized with the JSON dataset on startup.
def _load_blocked_users() -> None:
    global blocked_users
    dataset = _getting_dataset()
    blocked_users = {
        int(user_id)
        for user_id, record in dataset.items()
        if isinstance(record, dict) and record.get("is_blocked") is True
    }

    # Preserve the old hard-coded block only if that user is not already in the dataset.
    changed = False
    for user_id in LEGACY_BLOCKED_USERS:
        key = str(user_id)
        if key not in dataset:
            continue
        if not dataset[key].get("is_blocked", False):
            # Do not silently override a persisted explicit unblock.
            continue
        blocked_users.add(user_id)


_load_blocked_users()

# Rebuild the in-memory user list from the persistent dataset after a restart.
users_id = [int(uid) for uid in _getting_dataset().keys() if str(uid).isdigit()]

def sorting_users(ids):
    """Track a user for broadcasts while keeping the JSON dataset authoritative."""
    user_id = str(ids)
    ensure_user(user_id)
    numeric_id = int(ids)
    # if numeric_id not in users_id:
    #     users_id.append(numeric_id)
    #     bot.send_message(data_base_channel, f"New user has started the bot.\n{users_id}")

def converting_id_to_name():
    name_list = []
    users_id = list(_getting_dataset().keys())
    try:
        if len(users_id) == 0:
            bot.send_message(ADMIN_ID, "<b>No user found in the users id list</b>", parse_mode="HTML")
        elif len(users_id) > 0:
            for x in users_id:
                try: 
                   users_info = bot.get_chat(x)
                   name_list.append(users_info.first_name)
                except Exception as e:
                    bot.send_message(ADMIN_ID, f"Error in getting users {x} error {e}")
            bot.send_message(data_base_channel, f"The name of the users : {name_list}")
            bot.send_message(ADMIN_ID, "<b>The request is done.</b>", parse_mode="HTML")
    except Exception as e :
        bot.send_message(ADMIN_ID, f"error in {e}")


@bot.message_handler(commands=["start","spotify","link"])
@user_access_required
def starting(message : Message) -> None:
    try:
        data_set = _getting_dataset()
        user_id = str(message.from_user.id)
        text = message.text
        if user_id not in data_set.keys():
            processing_new_user(user_id)
        if not is_user_blocked(user_id) or user_id == ADMIN_ID:
            if text == "/spotify":
                markup = quick_markup({
                'play list': {'url': 'https://open.spotify.com/playlist/17zQ1hY55qJCOBnKU98hXS?si=-HiZaIOiSxW0gMFqbA26mw'} }, row_width=2)
                bot.send_message(message.from_user.id, "<b>Here is my playlist</b>", reply_markup=markup, parse_mode="HTML")
            elif text == "/start":
                bot.send_message(message.from_user.id, f"<b>Welcome <a href='tg://user?id={message.from_user.id}'>{message.from_user.first_name}</a></b>", parse_mode="HTML")
            elif text == "/link" and user_id == ADMIN_ID:
                markup = quick_markup({
                '🐈‍⬛': {
                    'url': 'https://t.me/talktoal_bot'}
                }, row_width=2)
                bot.send_message(ADMIN_ID,"<b><i>Talk to me</i></b>", reply_markup=markup, parse_mode="HTML")
        else:
            bot.send_message(user_id, "Sadly, you are blocked from using the bot :(")
        del data_set
    except Exception as e:
        bot.send_message(ADMIN_ID, f"There was and error {e}")


@bot.message_handler(commands=["$"])
def replying(message):
    if not _is_admin(message.from_user.id):
        bot.send_message(message.from_user.id, "<b>Only admin has the privilege of sending reply</b>", parse_mode="HTML")
        return

    args = message.text.split()
    if len(args) < 3 or not args[1].isdigit() or not args[2].isdigit():
        bot.reply_to(message, "Usage: /$ <message_id> <user_id>")
        return

    msg_id = int(args[1])
    the_id = int(args[2])
    bot.reply_to(message, f"Send your reply to {the_id}")
    bot.register_next_step_handler(message, lambda msg: sending_reply(msg, the_id, msg_id))


@user_access_required
def sending_reply(message, the_id, msg_id):
    if message.text == "cancel":
        bot.reply_to(message, "Replying has been cancelled.")
    else:
        try:
            bot.send_message(the_id, "<b><i>You have a new message from admin :</i></b>", parse_mode="HTML")
            bot.copy_message(the_id, message.from_user.id, message.id, reply_to_message_id=msg_id)
            bot.send_message(ADMIN_ID, f"<i>the reply to {the_id} was successful</i>", parse_mode="HTML")
        except Exception as e:
            bot.send_message(ADMIN_ID, f"we got a problem in replying {e}")


@bot.message_handler(commands=["block"])
def block_user(message: Message) -> None:
    if not _is_admin(message.from_user.id):
        bot.send_message(message.from_user.id, "Only admin has the privilege of blocking.")
        return

    args = message.text.split()
    if len(args) < 2 or not args[1].isdigit():
        bot.send_message(ADMIN_ID, "Usage: /block <user_id>")
        return

    user_id = args[1]
    try:
        dataset = _getting_dataset()
        if user_id not in dataset:
            bot.send_message(ADMIN_ID, f"The user {user_id} is not in the dataset.")
            return

        if set_user_blocked(user_id, True):
            markup = quick_markup(
                {"unblock": {"switch_inline_query_current_chat": f"/unblock {user_id}"}},
                row_width=1
            )
            bot.send_message(
                ADMIN_ID,
                f"<b>{user_id} is successfully blocked.</b>",
                parse_mode="HTML",
                reply_markup=markup
            )
    except Exception as e:
        bot.send_message(ADMIN_ID, f"An error occurred while blocking {user_id}: {e}")

@bot.message_handler(commands=["unblock"])
def unblocking(message: Message):
    if not _is_admin(message.from_user.id):
        bot.send_message(message.from_user.id, "You are not allowed.")
        return

    args = message.text.split()
    if len(args) < 2 or not args[1].isdigit():
        bot.send_message(ADMIN_ID, "Usage: /unblock <user_id>")
        return

    user_id = args[1]
    try:
        if set_user_blocked(user_id, False):
            bot.send_message(ADMIN_ID, f"User {user_id} is unblocked now.")
        else:
            bot.send_message(ADMIN_ID, f"User {user_id} is not in the dataset.")
    except Exception as e:
        bot.send_message(ADMIN_ID, f"Error in unblocking {user_id}: {e}")

@bot.message_handler(commands=["bio"])
@user_access_required
def bio(message):
    markup = quick_markup({
        'insta 📽️': {"url": "https://www.instagram.com/thetouyas?igsh=dDFibTlqbjB2c2N2"},
        "github 📟": {"url": "https://github.com/alimojarrad"},
        "gmail 📫": {"url": "https://mail.google.com/mail/?v"
                           "iew=cm&fs=1&to=alimojarrad2003@gmail.com&su=Subject&body=Body%20text"}
    }, row_width=3)
    if is_user_blocked(message.from_user.id):
        sorting_users(message.from_user.id)
        bot.send_message(message.from_user.id, "Sorry it looks like you have been blocked by admin :(")
        bot.send_message(ADMIN_ID, f"{message.from_user.id} tried messaging you while being blocked")
    else:
      bot.send_message(message.from_user.id, f"<b>Hello <a href='tg://user?id="
                                             f"{message.from_user.id}'>{message.from_user.first_name}</a>.\n"
                                           f"Thank you so much for using this bot.\n"
                                           f"If you want more contact @niyeznayu.</b>", parse_mode="HTML")
      bot.send_message(message.from_user.id, f"<b>Here are all of my socials.</b>", parse_mode="HTML", reply_markup=markup)


@bot.message_handler(commands=["dsbm"])
@user_access_required
def send_song(message):
    markup = quick_markup({
        'Thanks for listening.': {'url': 'https://t.me/thetouyas'}
    }, row_width=1)
    random_number = random.randrange(len(audio_list_dsbm))
    try:
        if not audio_list_dsbm:
            bot.reply_to(message, "No DSBM tracks are configured right now.")
            return
        sorting_users(message.from_user.id)
        audio_id = audio_list_dsbm[random_number]
        bot.reply_to(message, "Please wait a few moments")
        bot.send_audio(message.from_user.id, audio_id, reply_markup=markup)
    except Exception as e:
        bot.send_message(ADMIN_ID, f"There has been a problem with audio sending : {e}")


@bot.message_handler(commands=["jazz"])
@user_access_required
def send_song(message):
    markup = quick_markup({
        'Thanks for listening.': {'url': 'https://t.me/thetouyas'}
    }, row_width=1)
    random_number = random.randrange(len(jazz_list))
    try:
        if not jazz_list:
            bot.reply_to(message, "No jazz tracks are configured right now.")
            return
        sorting_users(message.from_user.id)
        audio_id = jazz_list[random_number]
        bot.reply_to(message, "Please wait a few moments")
        bot.send_audio(message.from_user.id, audio_id, reply_markup=markup)
    except Exception as e:
        bot.send_message(ADMIN_ID, f"There has been a problem with audio sending : {e}")
        bot.send_message(message.from_user.id, "oops, there has been a problem. Try again later.")


@bot.message_handler(commands=["song"])
@user_access_required
def send_song_list(message):
    try:
        sorting_users(message.from_user.id)
        bot.send_message(message.from_user.id, f"<b>Hello <a href='tg://user?id={message.from_user.id}'>{message.from_user.first_name}</a>\nHere is the full list of all the available music genres:\n/dsbm for dsbm\n/jazz for chilling jazz\nThe list will be updated.</b>", parse_mode="HTML")
    except Exception as e:
        bot.send_message(ADMIN_ID, f"There has been a problem in getting the song list : {e}")


@bot.message_handler(commands=["msg"])
@user_access_required
def intro(message : Message):
    try:
        markup = quick_markup({
            "cancel🚫": {"callback_data": "cancel"}
        }, row_width=1)
        if _is_admin(str(message.from_user.id)):
            bot.send_message(ADMIN_ID, "Hello, admin")
        elif not is_user_blocked(str(message.from_user.id)):
            bot.send_message(message.from_user.id , "<b>Hello\nSend your message to Admin\nSend /cancel to cancel sending.</b>", parse_mode="HTML")
            sorting_users(message.from_user.id)
            bot.register_next_step_handler(message, sending_message)
        if is_user_blocked(str(message.from_user.id)):
            bot.send_message(message.from_user.id, "<b>Oops it looks like you have been blocked</b>", parse_mode="HTML")
    except Exception as e :
        bot.reply_to(message, "There has been some error try again later")
        bot.send_message(ADMIN_ID, f"Error in sending message by /msg : {e}")


@user_access_required
def sending_message(message : Message):
    creepy_names = ["-", "-", ".", "..", "--", ",", "*", "!", "@", "#", "$", "%", "^", "&"]
    user_id = message.from_user.id
    user_info = bot.get_chat(user_id)
    name = user_info.first_name
    user_name = user_info.username
    bio = user_info.bio
    pfp = user_info.photo
    main_list = [bio, pfp, user_name]
    def getting_msg(message):
        bio = bot.get_chat(message.from_user.id).bio
        try:
            if not is_user_blocked(str(message.from_user.id)):
                if _is_admin(str(message.from_user.id)):
                    bot.send_message(ADMIN_ID, "<b>Hello Admin</b>", parse_mode="HTML")
                else:
                    user_stat.update({message.id: message.from_user.id})
                    bot.send_message(data_base_channel, f"users stats : {user_stat}")
                    bot.send_message(ADMIN_ID,
                                     f"<i><b>A message from '{message.from_user.id}' \n\nWith username: "
                                     f"'@{message.from_user.username}'\n\nbio: "
                                     f"'{bio}'\n\nWith first name: "
                                     f"'{message.from_user.first_name}' \n\n{time.ctime()}</b></i>",
                                     parse_mode="HTML")
                    markup = quick_markup({
                        'reply': {'callback_data': 'reply'},
                        'block': {'callback_data': f'block'},
                        'ban': {'switch_inline_query_current_chat': f'/ban {message.from_user.id}'},
                        'direct': {'switch_inline_query_current_chat': f'/dir {message.from_user.id}'}
                    }, row_width=2)
                    bot.copy_message(ADMIN_ID, message.from_user.id, message.id, reply_markup=markup)
                    bot.reply_to(message, "your message has been sent")
                    
        except Exception as e:
            bot.send_message(ADMIN_ID, f"There was a problem in getting messages {e}")
            bot.send_message(message.from_user.id, "Oops there has been an error try again later")
    if name not in creepy_names or any(main_list):
        if message.text == "/cancel":
         bot.reply_to(message, "The operation was cancelled.")
        else:
         getting_msg(message)
    else:
        user_stat.update({message.id: message.from_user.id})
        markup = quick_markup({
            'reply': {'callback_data': f'reply'},
            'block': {'callback_data': f'block'}
        }, row_width=2)
        bot.reply_to(message, "Sorry you look unknown (╯•﹏•╰)\nMaybe set a username or put pfp to send a message")
        bot.send_message(ADMIN_ID,
                         f"a user with no clear identity tried messaging you.\nname: "
                         f"{message.from_user.first_name}\nid: {message.from_user.id}",
                         reply_markup=markup)


@bot.message_handler(commands=["getuser"])
def sending_users(message):
    if _is_admin(message.from_user.id):
        dataset = _getting_dataset()
        bot.send_message(ADMIN_ID, f"{list(dataset.keys())}")
    else:
        bot.send_message(message.from_user.id, "You have no admin rights.")


@bot.message_handler(commands=["getblocked"])
def sending_users(message):
    if _is_admin(message.from_user.id):
        # bot.send_message(ADMIN_ID, f"{blocked_users}")
        dataset = _getting_dataset()
        names = []
        for k, v in dataset.items():
            if v['is_blocked']:
                names.append(v['name'])
        if len(names) == 0:
            bot.send_message(ADMIN_ID, "There are no blocked users")
        else:
            bot.send_message(ADMIN_ID, f"Here are the blocked users {names}")
        del dataset, names
    else:
        bot.send_message(message.from_user.id, "You have no admin rights.")


@bot.message_handler(commands=["getbanned"])
def sending_banned(message):
    if not _is_admin(message.from_user.id):
        bot.send_message(message.from_user.id, "You have no admin rights.")
        return
    try:
        bot.send_message(ADMIN_ID, f"{banned_users}")
    except Exception as e:
        bot.send_message(ADMIN_ID, f"Error getting banned users: {e}")


@bot.message_handler(commands=["tab"])
def identifying(message):
    if _is_admin(message.from_user.id):
        bot.send_message(ADMIN_ID, "send the password")
        bot.register_next_step_handler(message, password)
    else:
        bot.send_message(message.from_user.id , "you are not allowed")


def password(message):
    if ADMIN_PANEL_PASSWORD and message.text == ADMIN_PANEL_PASSWORD:
        bot.send_message(ADMIN_ID, "send your tab")
        bot.register_next_step_handler(message, sending_tab)
    else:
        bot.reply_to(message, "The password is wrong. The function has been cancelled.")


def sending_tab(message):
    bot.send_message(ADMIN_ID, "you have 60 seconds to make any changes in your tab")
    users_id = list(_getting_dataset().keys())
    time.sleep(60)
    bot.reply_to(message, "Times up!")
    for x in users_id:
      try:
        if not _is_admin(x) and is_user_blocked(x):
            bot.send_message(data_base_channel, f"skipped blocked user {x}")
            continue
        bot.copy_message(x,message.from_user.id, message.id)
        bot.send_message(data_base_channel, f"successfully sent to {x}")
      except Exception as e:
        bot.send_message(data_base_channel, f"unsuccessful  to {x} error {e}")
        continue


@bot.message_handler(commands=["anon"])
@user_access_required
def info(message):
    sorting_users(message.from_user.id)
    user_id = message.from_user.id
    channel_id = daily_channel
    try:
        member = bot.get_chat_member(channel_id, user_id)
        if member.status in ['member', 'administrator', 'creator']:
            bot.send_message(message.from_user.id, "Please send your song.")
            bot.register_next_step_handler(message, send_song)
        else:
            markup = quick_markup({"click here to check.☑️": {"callback_data": "join"}}, row_width=1)
            bot.send_message(user_id, f"Dear {message.from_user.first_name}, "
                                      f"in order to send a song you have to be a member of this channel @thetouyas", reply_markup=markup)
    except Exception as e:
        bot.send_message(ADMIN_ID, f"error in /anon as {e}")
        bot.reply_to(message, "Oops, there has been a problem try again later.")


@user_access_required
def send_song(message):
    markup = quick_markup({
        'Sent by anon.': {'url': 'https://t.me/thetouyas'}
    })
    banned_artist = ["Taylor Swift", "Ice Spice", "Amir Tataloo", "Shayea", "Zedbazi", "Unkown Artist",
                     "Mitski","6ix9ine", "Reza Pishro", "Ali Owj", "Sijal", "Behzad Leito", "Alireza JJ", "Saman Wilson"]
    try:
        if message.content_type == "audio":
            if message.audio.performer in banned_artist:
               bot.reply_to(message, "This artist is banned from being posted in this channel.")
            else:  
              bot.reply_to(message, "Your song has been sent.")
              audio_file = message.audio.file_id
              bot.send_audio(daily_channel, audio_file, reply_markup=markup)
              bot.send_message(ADMIN_ID, f"{message.from_user.id} {message.from_user.first_name} sent a song.")
        else:
            bot.reply_to(message, "only audio files are allowed.")
    except Exception as e:
        bot.send_message(ADMIN_ID, f"an Error in sending music by anon as {e}")
        bot.reply_to(message, "There has been an error try again later.")





@bot.message_handler(commands=["ban"])
def banning(message):
    if _is_admin(message.from_user.id):
        try:
            args = message.text.split()
            if len(args) > 1:
                userID = int(args[1])
                bot.ban_chat_member(daily_channel, userID)
                bot.reply_to(message, f"{userID} has been banned from @thetouyas")
                banned_users.append(userID)
                bot.send_message(data_base_channel, f"New user has been banned from daily channel {userID}")
            else:
                bot.reply_to(message, "Not valid arguments")
        except Exception as e:
            bot.send_message(ADMIN_ID, f"Error occurred in banning {e}")
    else:
        bot.send_message(message.from_user.id, "<b>Only admin has the privilege of banning</b>",
                         parse_mode="HTML")


@bot.message_handler(commands=["dir"])
def direct_msg(message):
    if not _is_admin(message.from_user.id):
        bot.send_message(message.from_user.id, "<b>Only admin has the privilege of sending direct</b>",
                         parse_mode="HTML")
        return

    args = message.text.split()
    if len(args) < 2 or not args[1].isdigit():
        bot.reply_to(message, "Usage: /dir <user_id>")
        return

    the_id = int(args[1])
    bot.send_message(ADMIN_ID, "Ready to send your direct message")
    bot.register_next_step_handler(message, lambda msg: sending_dir(msg, the_id))
def sending_dir(message, the_id):
    if message.text == "cancel":
        bot.reply_to(message, "Sending dir has been cancelled.")
    else:
        try:
            bot.send_message(the_id, "<b>You have a new message from admin :</b>", parse_mode="HTML")
            bot.copy_message(the_id, message.from_user.id, message.id)
            bot.send_message(ADMIN_ID, f"<i>the reply to {the_id} was successful</i>", parse_mode="HTML")
        except Exception as e:
            bot.send_message(ADMIN_ID, f"we got a problem in replying {e}")


@bot.message_handler(commands=['pannel'])
def showing_panel(message):
    try:
        markup = quick_markup({
            'users👤': {'callback_data': 'user'},
            'blocked🚷': {'callback_data': 'blocked'},
            'close❌': {'callback_data' : 'close'},
            'tab📊': {'callback_data': 'tab'},
            'names📃': {'callback_data': 'names'}
        }, row_width=2)
        dataset = _getting_dataset()
        total_user = len(dataset)
        total_blocked = len(["yes" for x, v in dataset.items() if v['is_blocked']])
        if _is_admin(message.from_user.id):
            bot.send_message(ADMIN_ID, f"<b>Hey👋\nYour bot has a total users of {total_user}.\nYour bot has blocked {total_blocked} users.\nBot running on pythonanywhere.com</b>", 
                             parse_mode="HTML", reply_markup=markup)
        else:
            bot.reply_to(message, "You are not allowed.")
    except Exception as e:
        bot.send_message(ADMIN_ID, f"Error in /pannel {e}")


@bot.callback_query_handler(func=lambda call: call.data == "names")
def sending_name(call):
    try:
        bot.send_message(ADMIN_ID, "<b>Processing your request</b>", parse_mode="HTML")
        names = []
        dataset = _getting_dataset()
        for k, v in dataset.items():
            names.append(v['name'])
        bot.send_message(data_base_channel, f"The name of the users : \n{names}")
        bot.send_message(ADMIN_ID, "required task is done")
    except Exception as e:
        bot.send_message(ADMIN_ID, f"There was a problem in the callback {e}")

@bot.callback_query_handler(func=lambda call:call.data == "user")
def sending_user(call):
    try:
        dataset = _getting_dataset()
        bot.send_message(data_base_channel, f'total users {list(dataset.keys())}')
        bot.send_message(ADMIN_ID, "<b> required task is done.</b>", parse_mode="HTML")
    except Exception as e:
        bot.send_message(ADMIN_ID, f"error in sending total users {e}")   


@bot.callback_query_handler(func=lambda call:call.data == "blocked")
def sending_blocked(call):
    try:
        dataset = _getting_dataset()
        names = []
        for k, v in dataset.items():
            if v['is_blocked']:
                names.append(v['name'])
        if len(names) == 0:
            bot.send_message(data_base_channel, "You have no blocked users")
        else:
            bot.send_message(data_base_channel, f'Total blokced users {names}')
        bot.send_message(ADMIN_ID, "<b>required task is done</b>", parse_mode="HTML")
    except Exception as e:
        bot.send_message(ADMIN_ID, f"error in sending total blocked as {e}")

@bot.callback_query_handler(func=lambda call:call.data == "close")
def closing_pannel(call):
    try:
        bot.delete_message(ADMIN_ID, call.message.id)
    except Exception as e:
        bot.send_message(ADMIN_ID, f"error in closing pannel {e}")


@bot.callback_query_handler(func=lambda call:call.data == "tab")
def getting_password(call):
    try:
        if _is_admin(call.from_user.id):
            bot.send_message(ADMIN_ID, f"Please send your password : ")
            bot.register_next_step_handler(call.message, password_call)
        else:
            bot.send_message(call.from_user.id, "You are not allowed.")
    except Exception as e:
        bot.send_message(ADMIN_ID, f"Error in tab {e}")
def password_call(message):
    if ADMIN_PANEL_PASSWORD and message.text == ADMIN_PANEL_PASSWORD:
        bot.send_message(ADMIN_ID, "send your tab")
        bot.register_next_step_handler(message, sending_tab_call)
    else:
        bot.reply_to(message, "The password is wrong. The function has been cancelled.")
def sending_tab_call(message):
    bot.send_message(ADMIN_ID, "you have 30 seconds to make any changes in your tab")
    time.sleep(30)
    bot.reply_to(message, "Times up!")
    dataset = _getting_dataset()
    for x in list(dataset.keys()):
      try:
        if not _is_admin(x) and is_user_blocked(x):
            bot.send_message(data_base_channel, f"skipped blocked user {x}")
            continue
        bot.copy_message(x,message.from_user.id, message.id)
        bot.send_message(data_base_channel, f"successfully sent to {x}")
      except Exception as e:
        bot.send_message(data_base_channel, f"unsuccessful  to {x} error {e}")
        continue
    del dataset


@bot.callback_query_handler(func=lambda call: call.data == "reply")
def reply_register(call):
    try:
        msg_id = call.message.id - 2
        bot.send_message(ADMIN_ID, "<b> Please send your reply</b>", parse_mode="HTML")
        bot.register_next_step_handler(call.message, lambda msg: process_user_reply(msg, msg_id))
    except Exception as e:
        bot.send_message(ADMIN_ID, f"An error occurred in callback data as {e}")
def process_user_reply(message, msg_id):
    try:
        admin_stat.update({message.id: int(ADMIN_ID)})
        markup = quick_markup({
            "reply": {"callback_data": "replyAdmin"}
        }, row_width=1)
        user_id = user_stat.get(msg_id)
        if user_id is None:
            bot.reply_to(message, "Could not identify the original user.")
            return
        if is_user_blocked(user_id):
            bot.reply_to(message, "That user is currently blocked.")
            return
        bot.send_message(user_id, f"<b>You have a reply from admin</b>", parse_mode="HTML")
        bot.copy_message(user_id, message.from_user.id, message.id, reply_to_message_id=msg_id)
        bot.reply_to(message, "Reply has been sent.")
        print(message.id)
    except Exception as e:
        bot.send_message(ADMIN_ID, f"Error in replying as {e}")
    

@bot.callback_query_handler(func=lambda call: call.data == "replyAdmin")
@callback_access_required
def send_reply_admin(call):
    try:
      if not is_user_blocked(call.from_user.id):
         msg_id = call.message.id - 2
         print(call.message.id)
         bot.send_message(call.from_user.id , f"Send your reply")
         bot.register_next_step_handler(call.message, lambda msg: process_admin_reply(msg, msg_id))
      else:
          bot.send_message(call.from_user.id, "Oops you are blocked")
    except Exception as e:
        bot.send_message(ADMIN_ID, f"Problem in to admin reply as {e}")
        bot.send_message(call.from_user.id, "There hass been a problem for the time being user /msg")

# working on it
@user_access_required
def process_admin_reply(message, msg_id):
    try:
        markup = quick_markup({
                        'reply': {'callback_data': 'reply'},
                        'block': {'callback_data': f'block'},
                        'ban': {'switch_inline_query_current_chat': f'/ban {message.from_user.id}'},
                        'direct': {'switch_inline_query_current_chat': f'/dir {message.from_user.id}'}
                    }, row_width=2)
        bot.copy_message(ADMIN_ID, message.from_user.id, message.id, reply_markup=markup, 
                         reply_to_message_id=msg_id)
        user_stat.update({message.id: message.from_user.id})
        bot.send_message(data_base_channel, f"users stats : {user_stat}")
        bot.reply_to(message, "Your reply has been sent.")
    except Exception as e:
        bot.reply_to(message, "Oops there has been a problem please try again later or use /msg")
        bot.send_message(ADMIN_ID, f"Error in client to admin reply as {e}")


@bot.callback_query_handler(func=lambda call: call.data == "block")
def blocking(call):
    if not _is_admin(call.from_user.id):
        bot.answer_callback_query(call.id, "You are not allowed.", show_alert=True)
        return

    try:
        msg_id = call.message.id - 2
        user_id = user_stat.get(msg_id)
        if user_id is None:
            bot.answer_callback_query(call.id, "Could not identify the user.", show_alert=True)
            return

        if is_user_blocked(user_id):
            bot.answer_callback_query(call.id, "This user is already blocked.")
            return

        if set_user_blocked(user_id, True):
            markup = quick_markup(
                {"unblock": {"switch_inline_query_current_chat": f"/unblock {user_id}"}},
                row_width=1
            )
            bot.send_message(
                ADMIN_ID,
                f"<b>{user_id} has been blocked.</b>",
                parse_mode="HTML",
                reply_markup=markup
            )
            bot.answer_callback_query(call.id, "User blocked.")
    except Exception as e:
        bot.send_message(ADMIN_ID, f"Error in blocking: {e}")

@bot.callback_query_handler(func=lambda call: call.data == "join")
@callback_access_required
def checking(call):
    user = call.from_user.id
    channel_id = daily_channel
    msg_id = call.message.id
    try:
        member = bot.get_chat_member(channel_id, user)
        is_member = _member_status_is_active(member.status)
        update_user_membership(str(user), is_member)
        if is_member:
            bot.delete_message(user, msg_id)
            bot.send_message(user, "<b>Welcome, now send the song : </b>", parse_mode="HTML")
            bot.register_next_step_handler(call.message, reply_song)
        else:
            bot.answer_callback_query(call.id, "you haven't joined yet", show_alert=True)
    except Exception as e:
        bot.send_message(ADMIN_ID, f"Error in callback data join {e}")
@user_access_required
def reply_song(message):
    markup = quick_markup({
        'Sent by anon.': {'url': 'https://t.me/thetouyas'}
    })
    try:
        if message.content_type == "audio":
            bot.reply_to(message, "Your song has been sent.")
            audio_file = message.audio.file_id
            bot.send_audio(daily_channel, audio_file, reply_markup=markup)
            bot.send_message(ADMIN_ID, f"{message.from_user.id} {message.from_user.first_name} sent a song.")
        else:
            bot.reply_to(message, "only audio files are allowed.")
    except Exception as e:
        bot.send_message(ADMIN_ID, f"an Error in sending music by anon as {e}")
        bot.reply_to(message, "There has been an error try again later.")


@bot.callback_query_handler(func=lambda call:call.data == "cancel")
@callback_access_required
def canceling(call):
    try:
        user = call.from_user.id
        msg_id = call.message.id
        bot.send_message(user, "<b>The operation was cancelled</b>", parse_mode="HTML")
        bot.delete_message(user, msg_id)
    except Exception as e :
        bot.send_message(ADMIN_ID, f"Error is cancelling replies as {e}")


@bot.message_handler(content_types=["text", "sticker", "location", "photo", "audio",
                                    "animation","video","contact","document","voice","venue","dice","video_note"])
@user_access_required
def echo_all(message):
    bot.reply_to(message, "Sorry I did not understand what you said."
                          "\nIf you want to send a message, send the command /msg.")


if __name__ == "__main__":
    print("The bot is starting to run.")
    bot.infinity_polling(skip_pending=True)