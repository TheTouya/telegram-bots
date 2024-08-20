import os
import random
import telebot
import time
import re
from telebot.util import quick_markup
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv('API_KEY')
bot = telebot.TeleBot(api_key, parse_mode=None)

admin_id = os.getenv('ADMIN_ID')
dsbm_files_id = os.getenv("DSBM_FILE_IDS")
jazz_files_id=os.getenv("JAZZ_FILE_IDS")
data_base_channel = os.getenv("DATA_BASE_CHANNEL")
daily_channel = os.getenv("THETOUYAS")
jazz_list = jazz_files_id.split(",")
audio_list_dsbm = dsbm_files_id.split(",")
the_time = time.time()
current_time = time.ctime(the_time)
blocked_users = [1717677479]
users_id = []
banned_users = []
user_stat = {}
def sorting_users(ids):
    if ids not in users_id:
        users_id.append(ids)
        bot.send_message(data_base_channel, f"New users has started the bot.\n{users_id}")
    else:
        pass


@bot.message_handler(commands=["start","spotify","link"])
def starting(message):
    for x in blocked_users:
        if x == message.from_user.id:
            bot.reply_to(message, "you are restricted")
            bot.send_message(admin_id, "A blocked user is begging to send a message")
    if message.from_user.id not in blocked_users:
        sorting_users(message.from_user.id)
        if message.text == "/spotify":
            markup = quick_markup({
                'play list': {'url': 'https://open.spotify.com'
                                     '/playlist/17zQ1hY55qJCOBnKU98hXS?si=-HiZaIOiSxW0gMFqbA26mw'}
            }, row_width=2)
            bot.send_message(message.from_user.id, "<b>Here is my playlist</b>", reply_markup=markup, parse_mode="HTML")
        elif message.from_user.id == 5892994739:
            bot.send_message(admin_id, "welcome admin")
        else:
            bot.send_message(message.from_user.id, f"<b>Welcome <a href='tg://user?id={message.from_user.id}'>{message.from_user.first_name}</a></b>", parse_mode="HTML")
        if message.text == "/link":
            markup = quick_markup({
                '🐈‍⬛': {
                    'url': 'https://t.me/talktoal_bot'}
            }, row_width=2)
            bot.send_message(admin_id,"<b><i>Talk to me</i></b>", reply_markup=markup, parse_mode="HTML")


@bot.message_handler(commands=["$"])
def replying(message):
    main_list = message.text.split()
    msg_id = int(main_list[1])
    the_id = int(main_list[2])
    if message.from_user.id == 5892994739:
      bot.reply_to(message, f"send your reply to {the_id}")
      bot.register_next_step_handler(message, lambda msg : sending_reply(msg , the_id, msg_id))
    else:
        bot.send_message(message.from_user.id, "<b>Only admin has the privilege of sending reply</b>", parse_mode="HTML")


def sending_reply(message, the_id, msg_id):
    if message.text == "cancel":
        bot.reply_to(message, "Replying has been cancelled.")
    else:
        try:
            bot.send_message(the_id, "<b><i>You have a new message from admin :</i></b>", parse_mode="HTML")
            bot.copy_message(the_id, message.from_user.id, message.id, reply_to_message_id=msg_id)
            bot.send_message(admin_id, f"<i>the reply to {the_id} was successful</i>", parse_mode="HTML")
        except Exception as e:
            bot.send_message(admin_id, f"we got a problem in replying {e}")


@bot.message_handler(commands=["block"])
def block_user(message):
    id_user = re.search(r"\d{6,}",message.text)
    try:
      markup = quick_markup( {'unblock': {'switch_inline_query_current_chat': f'/unblock {id_user.group()}'}})
      if message.from_user.id == 5892994739:
        blocked_users.append(int(id_user.group()))
        bot.send_message(admin_id, f"The user {id_user.group()} has been blocked", reply_markup=markup)
        bot.forward_message(admin_id,message.from_user.id,message.id)
        print(blocked_users)
      else:
          bot.send_message(message.from_user.id, "<b>Only admin has the privilege of blocking</b>", parse_mode="HTML")
    except Exception as e:
        bot.send_message(admin_id, f"An error occurred in blocking : {e}")


@bot.message_handler(commands=["bio"])
def bio(message):
    markup = quick_markup({
        'insta 📽️': {"url": "https://www.instagram.com/thetouyas?igsh=dDFibTlqbjB2c2N2"},
        "github 📟": {"url": "https://github.com/TheTouya"},
        "gmail 📫": {"url": "https://mail.google.com/mail/?v"
                           "iew=cm&fs=1&to=alimojarrad2003@gmail.com&su=Subject&body=Body%20text"}
    }, row_width=3)
    if message.from_user.id in blocked_users:
        sorting_users(message.from_user.id)
        bot.send_message(message.from_user.id, "Sorry it looks like you have been blocked by admin :(")
        bot.send_message(admin_id, f"{message.from_user.id} tried messaging you while being blocked")
    else:
      bot.send_message(message.from_user.id, f"<b>Hello <a href='tg://user?id="
                                             f"{message.from_user.id}'>{message.from_user.first_name}</a>.\n"
                                           f"Thank you so much for using this bot.\n"
                                           f"If you want more contact @niyeznayu.</b>", parse_mode="HTML")
      bot.send_message(message.from_user.id, f"<b>Here are all of my socials.</b>", parse_mode="HTML", reply_markup=markup)


@bot.message_handler(commands=["dsbm"])
def send_song(message):
    markup = quick_markup({
        'Thanks for listening.': {'url': 'https://t.me/thetouyas'}
    }, row_width=1)
    random_number = random.randint(0,20)
    try:
        sorting_users(message.from_user.id)
        audio_id = audio_list_dsbm[random_number]
        bot.reply_to(message, "Please wait a few moments")
        bot.send_audio(message.from_user.id, audio_id, reply_markup=markup)
    except Exception as e:
        bot.send_message(admin_id, f"There has been a problem with audio sending : {e}")


@bot.message_handler(commands=["jazz"])
def send_song(message):
    markup = quick_markup({
        'Thanks for listening.': {'url': 'https://t.me/thetouyas'}
    }, row_width=1)
    random_number = random.randint(0,len(jazz_list))
    try:
        sorting_users(message.from_user.id)
        audio_id = jazz_list[random_number]
        bot.reply_to(message, "Please wait a few moments")
        bot.send_audio(message.from_user.id, audio_id, reply_markup=markup)
    except Exception as e:
        bot.send_message(admin_id, f"There has been a problem with audio sending : {e}")
        bot.send_message(message.from_user.id, "oops, there has been a problem. Try again later.")


@bot.message_handler(commands=["song"])
def send_song_list(message):
    try:
        sorting_users(message.from_user.id)
        bot.send_message(message.from_user.id, f"<b>Hello <a href='tg://user?id={message.from_user.id}'>{message.from_user.first_name}</a>\nHere is the full list of all the avaible music genres:\n/dsbm for dsbm\n/jazz for chilling jazz\nThe list will be updated.</b>", parse_mode="HTML")
    except Exception as e:
        bot.send_message(admin_id, f"There has been a problem in getting the song list : {e}")


@bot.message_handler(commands=["msg"])
def intro(message):
    try:
        if message.from_user.id == 5892994739:
            bot.send_message(admin_id, "Hello, admin")
        elif message.from_user.id not in blocked_users:
            bot.send_message(message.from_user.id , f"<b>Hello  \nSend your message to Admin</b>", parse_mode="HTML")
            sorting_users(message.from_user.id)
            bot.register_next_step_handler(message, sending_message)
        if message.from_user.id in blocked_users:
            bot.send_message(message.from_user.id, "<b>Oops it looks like you have been blocked</b>", parse_mode="HTML")
    except Exception as e :
        bot.reply_to(message, "There has been some error try again later")
        bot.send_message(admin_id, f"Error in sending message by /msg : {e}")


def sending_message(message):
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
            for x in blocked_users:
                if x == message.from_user.id:
                    bot.reply_to(message, "It looks like you have been blocked by the Admin :(")
                    bot.send_message(admin_id, f"{message.from_user.id} tried messaging you while being blocked")
            if message.from_user.id not in blocked_users:
                if message.from_user.id == 5892994739:
                    bot.send_message(admin_id, "<b>Hello Admin</b>", parse_mode="HTML")
                else:
                    user_stat.update({message.id: message.from_user.id})
                    bot.send_message(admin_id,
                                     f"<i><b>A message from '{message.from_user.id}' \n\nWith username: "
                                     f"'@{message.from_user.username}'\n\nbio: "
                                     f"'{bio}'\n\nWith first name: "
                                     f"'{message.from_user.first_name}' \n\n{current_time}</b></i>",
                                     parse_mode="HTML")
                    markup = quick_markup({
                        'reply': {'callback_data': 'reply'},
                        'block': {'callback_data': f'block'},
                        'ban': {'switch_inline_query_current_chat': f'/ban {message.from_user.id}'},
                        'direct': {'switch_inline_query_current_chat': f'/dir {message.from_user.id}'}
                    }, row_width=2)
                    bot.copy_message(admin_id, message.from_user.id, message.id, reply_markup=markup)
                    bot.reply_to(message, "your message has been sent")
                    
        except Exception as e:
            bot.send_message(admin_id, f"There was a problem in getting messages {e}")
            bot.send_message(message.from_user.id, "Oops there has been an error try again later")
    if name not in creepy_names or any(main_list):
        getting_msg(message)
    else:
        user_stat.update({message.id: message.from_user.id})
        markup = quick_markup({
            'reply': {'callback_data': f'reply'},
            'block': {'callback_data': f'block'}
        }, row_width=2)
        bot.reply_to(message, "Sorry you look unknown (╯•﹏•╰)\nMaybe set a username or put pfp to send a message")
        bot.send_message(admin_id,
                         f"a user with no clear identity tried messaging you.\nname: "
                         f"{message.from_user.first_name}\nid: {message.from_user.id}",
                         reply_markup=markup)


@bot.message_handler(commands=["getuser"])
def sending_users(message):
    if message.from_user.id == 5892994739:
        bot.send_message(admin_id, f"{users_id}")
    else:
        bot.send_message(message.from_user.id, "You have no admin rights.")


@bot.message_handler(commands=["getblocked"])
def sending_users(message):
    if message.from_user.id == 5892994739:
        bot.send_message(admin_id, f"{blocked_users}")
    else:
        bot.send_message(message.from_user.id, "You have no admin rights.")


@bot.message_handler(commands=["getbanned"])
def sending_banned(message):
    try:
        bot.send_message(admin_id, f"{banned_users}")
    except Exception as e:
        bot.reply_to(message, f"error as {e}")


@bot.message_handler(commands=["tab"])
def identifying(message):
    if message.from_user.id == 5892994739:
        bot.send_message(admin_id, "send the password")
        bot.register_next_step_handler(message, pasword)
    else:
        bot.send_message(message.from_user.id , "you are not allowed")


def pasword(message):
    if message.text == "ali5282":
        bot.send_message(admin_id, "send your tab")
        bot.register_next_step_handler(message, sending_tab)
    else:
        bot.reply_to(message, "The password is wrong. The function has been cancelled.")


def sending_tab(message):
    bot.send_message(admin_id, "you have 30 seconds to make any changes in your tab")
    time.sleep(30)
    bot.reply_to(message, "Times up!")
    for x in users_id:
      try:
        bot.copy_message(x,message.from_user.id, message.id)
        bot.send_message(data_base_channel, f"successfully sent to {x}")
      except Exception as e:
        bot.send_message(data_base_channel, f"unsuccessful  to {x} error {e}")
        continue


@bot.message_handler(commands=["anon"])
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
        bot.send_message(admin_id, f"error in /anon as {e}")
        bot.reply_to(message, "Oops, there has been a problem try again later.")


def send_song(message):
    markup = quick_markup({
        'Sent by anon.': {'url': 'https://t.me/thetouyas'}
    })
    try:
        if message.content_type == "audio":
            bot.reply_to(message, "Your song has been sent.")
            audio_file = message.audio.file_id
            bot.send_audio(daily_channel, audio_file, reply_markup=markup)
            bot.send_message(admin_id, f"{message.from_user.id} {message.from_user.first_name} sent a song.")
        else:
            bot.reply_to(message, "only audio files are allowed.")
    except Exception as e:
        bot.send_message(admin_id, f"an Error in sending music by anon as {e}")
        bot.reply_to(message, "There has been an error try again later.")


@bot.message_handler(commands=['unblock'])
def unblocking(message):
    if message.from_user.id == 5892994739:
        try:
            txt_list = message.text.split()
            blocked_users.remove(int(txt_list[1]))
            bot.send_message(admin_id, f"User {txt_list[1]} is unblocked now")
        except Exception as e:
            bot.reply_to(message, f"error in unblocking as {e}")
    else:
        bot.send_message(message.from_user.id, "You are not allowed.")


@bot.message_handler(commands=["ban"])
def banning(message):
    if message.from_user.id == 5892994739:
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
            bot.send_message(admin_id, f"Error occurred in banning {e}")
    else:
        bot.send_message(message.from_user.id, "<b>Only admin has the privilege of banning</b>",
                         parse_mode="HTML")


@bot.message_handler(commands=["dir"])
def direct_msg(message):
    main_list = message.text.split()
    the_id = int(main_list[1])
    if message.from_user.id == 5892994739:
        bot.send_message(admin_id, "Ready to send your direct message")
        bot.register_next_step_handler(message, lambda msg : sending_dir(msg , the_id))
    else:
        bot.send_message(message.from_user.id, "<b>Only admin has the privilege of sending direct</b>",
                         parse_mode="HTML")
def sending_dir(message, the_id):
    if message.text == "cancel":
        bot.reply_to(message, "Sending dir has been cancelled.")
    else:
        try:
            bot.send_message(the_id, "<b>You have a new message from admin :</b>", parse_mode="HTML")
            bot.copy_message(the_id, message.from_user.id, message.id)
            bot.send_message(admin_id, f"<i>the reply to {the_id} was successful</i>", parse_mode="HTML")
        except Exception as e:
            bot.send_message(admin_id, f"we got a problem in replying {e}")


@bot.callback_query_handler(func=lambda call: call.data == "reply")
def reply_register(call):
    try:
        msg_id = call.message.id - 2
        print(msg_id)
        bot.send_message(admin_id, "<b> Please send your reply</b>", parse_mode="HTML")
        bot.register_next_step_handler(call.message, lambda msg: process_user_reply(msg, msg_id))
    except Exception as e:
        bot.send_message(admin_id, f"An error occurred in callback data as {e}")
def process_user_reply(message, msg_id):
    try:
        user_id = user_stat.get(msg_id)
        bot.send_message(user_id, f"<b>You have a reply from admin</b>", parse_mode="HTML")
        bot.copy_message(user_id, message.from_user.id, message.id, reply_to_message_id=msg_id)
        bot.reply_to(message, "Reply has been sent.")
    except Exception as e:
        bot.send_message(admin_id, f"Error in replying as {e}")
    

@bot.callback_query_handler(func=lambda call: call.data == "replyAdmin")
def send_reply_admin(call):
    try:
      if call.from_user.id not in blocked_users:
         bot.send_message(call.from_user.id , f"Send your reply {call.from_user.first_name}")
         bot.register_next_step_handler(call.message, admin_replier)
      else:
          bot.send_message(call.from_user.id, "Oops you are blocked")
    except Exception as e:
        bot.send_message(admin_id, f"Problem in to admin reply as {e}")
        bot.send_message(call.from_user.id, "There hass been a problem for the time being user /msg")


def admin_replier(message):
    markup = quick_markup({
                        'reply': {'callback_data': 'reply'},
                        'block': {'callback_data': f'block'},
                        'ban': {'switch_inline_query_current_chat': f'/ban {message.from_user.id}'},
                        'direct': {'switch_inline_query_current_chat': f'/dir {message.from_user.id}'}
                    }, row_width=2)
    msg_id = bot.user_data.get("admin")
    bot.user_data = {"user_id": message.from_user.id, "msg_id": message.id}
    
    try:
        markup = quick_markup({
                        'reply': {'callback_data': 'reply'},
                        'block': {'callback_data': f'block'},
                        'ban': {'switch_inline_query_current_chat': f'/ban {message.from_user.id}'},
                        'direct': {'switch_inline_query_current_chat': f'/dir {message.from_user.id}'}
                    }, row_width=2)
        bot.copy_message(admin_id, message.from_user.id, message.id, reply_to_message_id=msg_id, reply_markup=markup)
        bot.reply_to(message, "Your reply has been sent.")
        bot.user_data = {"user_id": message.from_user.id, "msg_id": message.id}
    except Exception as e:
        bot.reply_to(message, "Oops there has been a problem please try again later or use /msg")
        bot.send_message(admin_id, "Error in client to admin reply as {e}")


@bot.callback_query_handler(func=lambda call: call.data == "block")
def blocking(call):
    try:
        msg_id = call.message.id - 2
        user_id = user_stat.get(msg_id)
        if user_id not in blocked_users:
            blocked_users.append(int(user_id))
            markup = quick_markup( {'unblock': {'switch_inline_query_current_chat': f'/unblock {user_id}'}})
            bot.send_message(admin_id, f"<b>{user_id} has been blocked</b>", parse_mode="HTML", reply_markup=markup)
        elif user_id in blocked_users:
            bot.send_message(admin_id, f"the user {user_id} has already been blocked.")
    except Exception as e:
        bot.send_message(admin_id, f"error in blocking {e}")


@bot.callback_query_handler(func=lambda call: call.data == "join")
def checking(call):
    user = call.from_user.id
    channel_id = daily_channel
    msg_id = call.message.id
    try:
        member = bot.get_chat_member(channel_id, user)
        if member.status in ['member', 'administrator', 'creator']:
            bot.delete_message(user, msg_id)
            bot.send_message(user, "</b>Welcome, now send the song : </b>", parse_mode="HTML")
            bot.register_next_step_handler(call.message, reply_song)
        else:
            bot.send_message(user, "You didn't join yet. Please try again.")
    except Exception as e:
        bot.send_message(admin_id, f"Error in callback data join {e}")
def reply_song(message):
    markup = quick_markup({
        'Sent by anon.': {'url': 'https://t.me/thetouyas'}
    })
    try:
        if message.content_type == "audio":
            bot.reply_to(message, "Your song has been sent.")
            audio_file = message.audio.file_id
            bot.send_audio(daily_channel, audio_file, reply_markup=markup)
            bot.send_message(admin_id, f"{message.from_user.id} {message.from_user.first_name} sent a song.")
        else:
            bot.reply_to(message, "only audio files are allowed.")
    except Exception as e:
        bot.send_message(admin_id, f"an Error in sending music by anon as {e}")
        bot.reply_to(message, "There has been an error try again later.")

@bot.message_handler(content_types=["text", "sticker", "location", "photo", "audio",
                                    "animation","video","contact","document","voice","venue","dice","video_note"])
def echo_all(message):
    bot.reply_to(message, "Sorry I did not understand what you said."
                          "\nIf you want to send a message, send the command /msg.")


bot.infinity_polling()