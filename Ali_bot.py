import os
import random
import telebot
import time
import re
from quote import quote
from telebot.util import quick_markup
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv('API_KEY')
bot = telebot.TeleBot(api_key, parse_mode=None)

admin_id = os.getenv('ADMIN_ID')
dsbm_files_id = os.getenv("DSBM_FILE_IDS")
jazz_files_id=os.getenv("JAZZ_FILE_IDS")
jazz_list = jazz_files_id.split(",")
audio_list_dsbm = dsbm_files_id.split(",")
the_time = time.time()
current_time = time.ctime(the_time)
blocked_users = [1717677479]


# @bot.message_handler(content_types=["text"])
# def get_info(message):
#     user_id = message.from_user.id
#     user_info = bot.get_chat(user_id)
#     bio = user_info.bio if hasattr(user_info, 'bio') else "no bio"
#     bot.send_message(admin_id, f"{user_info.birthdate.day} {user_info.photo} {user_info.birthdate.month} {user_info.bio}")
    # bot.send_photo(admin_id, user_info.photo)
@bot.message_handler(commands=["start","me","link"])
def starting(message):
    for x in blocked_users:
        if x == message.from_user.id:
            bot.reply_to(message, "you are restricted")
            bot.send_message(admin_id, "A blocked user is begging to send a message")
    if message.from_user.id not in blocked_users:
        if message.text == "/me":
            markup = quick_markup({
                'play list': {'url': 'https://open.spotify.com/playlist/17zQ1hY55qJCOBnKU98hXS?si=-HiZaIOiSxW0gMFqbA26mw'}
            }, row_width=2)
            bot.send_message(message.from_user.id, "<b>Here is my playlist</b>", reply_markup=markup, parse_mode="HTML")
        elif message.from_user.id == 5892994739:
            bot.send_message(admin_id, "welcome admin")
        else:
            bot.send_message(message.from_user.id, f"<b>Welcome <a href='tg://user?id={message.from_user.id}'>{message.from_user.first_name}</a>\n"
                                                   f"Please send your message </b>", parse_mode="HTML")
        if message.text == "/link":
            markup = quick_markup({
                '🐈‍⬛': {
                    'url': 'https://t.me/talktoal_bot'}
            }, row_width=2)
            bot.send_message(admin_id,"<b><i>Talk to me</i></b>", reply_markup=markup, parse_mode="HTML")

    # bot.send_message(admin_id, f" a message from '{message.from_user.id}")


@bot.message_handler(commands=["$"])
def replying(message):
    id_user = re.search(r"\d{6,}", message.text)
    the_msg = re.findall(r"[^/$\d{6,}]", message.text)
    reply = '  '
    for x in the_msg:
        reply += x
    print(reply)
    try:
     if message.from_user.id == 5892994739 :
         bot.send_message(int(id_user.group()), "<b><i>You have a new message from admin :</i></b>", parse_mode="HTML")
         bot.send_message(int(id_user.group()), reply, protect_content=True)
         bot.reply_to(message, "Your message has been sent")
     else:
         bot.send_message(message.from_user.id, "<b>Only admin has the privilege of replying</b>", parse_mode="HTML")
    except Exception as e:
        bot.send_message(admin_id, f"An error occurred in replying : {e}")


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
        audio_id = jazz_list[random_number]
        bot.reply_to(message, "Please wait a few moments")
        bot.send_audio(message.from_user.id, audio_id, reply_markup=markup)
    except Exception as e:
        bot.send_message(admin_id, f"There has been a problem with audio sending : {e}")
        bot.send_message(message.from_user.id, "oops, there has been a problem. Try again later.")


@bot.message_handler(commands=["song"])
def send_song_list(message):
    try:
        bot.send_message(message.from_user.id, f"<b>Hello <a href='tg://user?id={message.from_user.id}'>{message.from_user.first_name}</a>\nHere is the full list of all the avaible music genres:\n/dsbm for dsbm\n/jazz for chilling jazz\nThe list will be updated.</b>", parse_mode="HTML")
    except Exception as e:
        bot.send_message(admin_id, f"There has been a problem in getting the song list : {e}")


@bot.message_handler(commands=["quote"])
def send_quote(message):
    message_list = message.text.split()
    print(message_list)
    authors_list = ["George Orwell", "Fyodor Dostoevsky", "Franz Kafka", "Albert Camus",
                    "Leo Tolstoy", "Mark Twain", "Steve Toltz", "Charles Dickens", "William Shakespeare",
                    "Dante Alighieri", "Marcus Aurelius", "Albert Camus", "Franz kafka", "Friedrich Nietzsche"]
    markup = quick_markup({
        'Have a great reading.': {'url': 'https://t.me/thetouyas'}
    }, row_width=1)
    random_author = random.randint(0,13)
    bot.reply_to(message, "This might take longer than usual.")
    try:
        if len(message_list) == 1:
            random_number = random.randint(0, 19)
            random_quote = quote(search=authors_list[random_author])
            bot.send_message(message.from_user.id, f"<b>{random_quote[random_number].get("quote")}</b>\n<i>{random_quote[random_number].get("author")}\n{random_quote[random_number].get("book")}</i>", parse_mode="HTML", reply_markup=markup)
        elif len(message_list) > 1:
            message_list.pop(0)
            text = ' '.join(message_list)
            random_quotes = quote(search=text)
            length = len(random_quotes)
            random_number = random.randint(0, length)
            bot.send_message(message.from_user.id, f"<b>{random_quotes[random_number].get("quote")}</b>\n<i>{random_quotes[random_number].get("author")}\n{random_quotes[random_number].get("book")}</i>", parse_mode="HTML", reply_markup=markup)

    except Exception as e:
        bot.send_message(admin_id, f"There has been a problem in quoting : {e}")
        bot.send_message(message.from_user.id, "Oops, there has been a problem, try again.")


@bot.message_handler(content_types=["text", "sticker", "location", "photo", "audio","animation","video","contact","document","voice","venue","dice","video_note"])
def send_message(message):
    creepy_names = ["-","-", ".", "..", "--", ",", "*", "!", "@", "#", "$", "%", "^", "&"]
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
        bot.reply_to(message, "Sorry you look unknown (╯•﹏•╰)\nMaybe set an username or put pfp to send a message")
        bot.send_message(admin_id, f"a user with no clear identity tried messaging you.\nname: {message.from_user.first_name}\nid: {message.from_user.id}", reply_markup=markup)


bot.infinity_polling()