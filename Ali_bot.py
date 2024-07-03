import os
import telebot
import time
import re
from telebot.util import quick_markup
bot = telebot.TeleBot('6945559888:AAFWc1Fv9r300hfn343Nci2sFCCqd6tgwwQ', parse_mode=None)


admin_id = 5892994739



the_time = time.time()
current_time = time.ctime(the_time)
blocked_users = [1717677479]


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
        elif message.from_user.id == admin_id:
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
    id_user = re.search(r"\d{8,}", message.text)
    the_msg = re.findall(r"[^/$\d{8,}]", message.text)
    reply = '  '
    for x in the_msg:
        reply += x
    print(reply)
    bot.send_message(int(id_user.group()), "<b><i>You have a new message from admin :</i></b>",parse_mode="HTML")
    bot.send_message(int(id_user.group()), reply, protect_content=True)
    bot.reply_to(message,"Your message has been sent")


@bot.message_handler(commands=["block"])
def block_user(message):
    print(message.text)
    id_user = re.search(r"\d{10}",message.text)
    print(id_user.group())
    blocked_users.append(int(id_user.group()))
    bot.reply_to(message, "this user user is blocked")
    bot.forward_message(admin_id,message.from_user.id,message.id)
    print(blocked_users)


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
                                           f"If you want more contact @niyeznayu</b>", parse_mode="HTML")
      bot.send_message(message.from_user.id, f"<b>Here are all of my socials.</b>", parse_mode="HTML", reply_markup=markup)


@bot.message_handler(content_types=["text", "sticker", "location", "photo", "audio","animation","video","contact","document","voice","venue","dice","video_note"])
def send_message(message):
    for x in blocked_users:
        if x == message.from_user.id:
            bot.reply_to(message, "It looks like you have been blocked by the Admin :(")
            bot.send_message(admin_id,f"{message.from_user.id} tried messaging you while being blocked")
    if message.from_user.id not in blocked_users:
        if message.from_user.id == admin_id:
            bot.send_message(admin_id,"<b>Hello Admin</b>", parse_mode="HTML")
        else:
            bot.send_message(admin_id,
         f"<i><b>A message from '{message.from_user.id}' \n\nWith username: "
                f"'@{message.from_user.username}' \n\nWith first name: '{message.from_user.first_name}' \n\n{current_time}</b></i>", parse_mode="HTML")
            bot.copy_message(admin_id, message.from_user.id, message.id)
            markup = quick_markup({
             'reply': {'switch_inline_query_current_chat': f'/$ {message.from_user.id}'},
             'block': {'switch_inline_query_current_chat': f'/block {message.from_user.id}'}
           }, row_width=2)
            bot.send_message(admin_id, f"<i>{message.from_user.id}</i>", reply_markup=markup, parse_mode="HTML")
            bot.reply_to(message, "your message has been sent")


bot.infinity_polling()
