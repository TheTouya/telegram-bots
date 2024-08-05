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
users_id = [5892994739, 5219712714, 5721051983, 6150578275,
            7373751883, 5716748441, 6670745719, 6593899683, 7462503512, 290749429, 214788532]


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
                'play list': {'url': 'https://open.spotify.com/playlist/17zQ1hY55qJCOBnKU98hXS?si=-HiZaIOiSxW0gMFqbA26mw'}
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
    the_id = int(main_list[1])
    if message.from_user.id == 5892994739:
      bot.reply_to(message, f"send your reply to {the_id}")
      bot.register_next_step_handler(message, lambda msg : sending_reply(msg , the_id))
    else:
        bot.send_message(message.from_user.id, "<b>Only admin has the privilege of sending reply</b>", parse_mode="HTML")


def sending_reply(message, the_id):
    try:
        bot.send_message(the_id, "<b><i>You have a new message from admin :</i></b>", parse_mode="HTML")
        bot.copy_message(the_id, message.from_user.id, message.id)
        bot.send_message(admin_id, f"<i>the reply to {the_id} was successful</i>", parse_mode="HTML")
    except Exception as e:
        bot.send_message(admin_id, f"we got a problem in replying {e}")


@bot.message_handler(commands=["block"])
def block_user(message):
    id_user = re.search(r"\d{6,}",message.text)
    try:
      if message.from_user.id == 5892994739:
        blocked_users.append(int(id_user.group()))
        bot.reply_to(message, "this user has been blocked")
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
        "gmail 📫": {"url": "https://mail.google.com/mail/?view=cm&fs=1&to=alimojarrad2003@gmail.com&su=Subject&body=Body%20text"}
    }, row_width=3)
    if message.from_user.id in blocked_users:
        sorting_users(message.from_user.id)
        bot.send_message(message.from_user.id, "Sorry it looks like you have been blocked by admin :(")
        bot.send_message(admin_id, f"{message.from_user.id} tried messaging you while being blocked")
    else:
      bot.send_message(message.from_user.id, f"<b>Hello <a href='tg://user?id={message.from_user.id}'>{message.from_user.first_name}</a>.\n"
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
        if message.from_user.id not in blocked_users:
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
                    bot.send_message(admin_id,
                                     f"<i><b>A message from '{message.from_user.id}' \n\nWith username: "
                                     f"'@{message.from_user.username}'\n\nbio: '{bio}'\n\nWith first name: '{message.from_user.first_name}' \n\n{current_time}</b></i>",
                                     parse_mode="HTML")
                    bot.copy_message(admin_id, message.from_user.id, message.id)
                    markup = quick_markup({
                        'reply': {'switch_inline_query_current_chat': f'/$ {message.from_user.id}'},
                        'block': {'switch_inline_query_current_chat': f'/block {message.from_user.id}'}
                    }, row_width=2)
                    bot.send_message(admin_id, f"<i>{message.from_user.id}</i>", reply_markup=markup, parse_mode="HTML")
                    bot.reply_to(message, "your message has been sent")
        except Exception as e:
            bot.send_message(admin_id, f"There was a problem in getting messages {e}")
            bot.send_message(message.from_user.id, "Oops there has been an error try again later")
    if name not in creepy_names or any(main_list):
        getting_msg(message)
    else:
        markup = quick_markup({
            'reply': {'switch_inline_query_current_chat': f'/$ {message.from_user.id}'},
            'block': {'switch_inline_query_current_chat': f'/block {message.from_user.id}'}
        }, row_width=2)
        bot.reply_to(message, "Sorry you look unknown (╯•﹏•╰)\nMaybe set a username or put pfp to send a message")
        bot.send_message(admin_id,
                         f"a user with no clear identity tried messaging you.\nname: {message.from_user.first_name}\nid: {message.from_user.id}",
                         reply_markup=markup)


@bot.message_handler(commands=["getuser"])
def sending_users(message):
    if message.from_user.id == admin_id:
        bot.send_message(admin_id, f"{users_id}")
    else:
        bot.send_message(message.from_user.id, "You have no admin rights.")


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
            bot.reply_to(message, "You have to be a member of the main channel to send a song @thetouyas")
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


@bot.message_handler(func=lambda m : True)
def echo_all(message):
    bot.reply_to(message, "Sorry I did not understand what you said.\nIf you want to send a message, send the command /msg.")


bot.infinity_polling()