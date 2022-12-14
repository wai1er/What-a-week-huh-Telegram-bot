import os
import time
from datetime import datetime
from random import randint
import telebot
import threading
from constants import *
import sqlite3
import logging

BOT = telebot.TeleBot(TOKEN)
DB = sqlite3.connect('users.db', check_same_thread=False)
CURSOR = DB.cursor()

logger = telebot.logger
telebot.logger.setLevel(logging.INFO)
logging.basicConfig(filename=LOG_PATH, level=logging.INFO,
                    format=' %(asctime)s - %(levelname)s - %(message)s')

"""

Creation of table of users in database
c.execute("CREATE TABLE users (user_name TEXT, chat_id INT, amount_of_text_messages INT DEFAULT 0)")
DB.commit()

"""


@BOT.message_handler(commands=["start"])
def handle_start_command(message):
    user_name, user_id = message.chat.username, message.chat.id

    CURSOR.execute("SELECT chat_id FROM users")

    chat_id_tuples = CURSOR.fetchall()
    chat_id_int = [chat_id[0] for chat_id in chat_id_tuples]

    if user_id not in chat_id_int:
        if user_name != None:
            CURSOR.execute(f"INSERT INTO users VALUES('{user_name}', {user_id}, {0})")
            DB.commit()
            BOT.send_message(user_id, f"Hello, captain {user_name}...")
            logger.info(f"New registered user: {user_name}, chat_id - {user_id}")
        else:
            CURSOR.execute(f"INSERT INTO users VALUES('{user_id}', {user_id}, {0})")
            DB.commit()
            BOT.send_message(user_id, f"Hello, stranger {point_right}{point_left}...")
            logger.info(f"New registered user: {user_id}, chat_id - {user_id}")
    else:
        BOT.send_message(user_id, "Already registered")
        logger.info(f"Already registered user: {user_name}, chat_id - {user_id}")

@BOT.message_handler(commands=["status"])
def handle_status_command(message):
    user_id = message.chat.id
    if user_id != ADMIN_CHAT_ID:
        BOT.send_message(
            user_id, "No, captain. You've entered the wrong door.")
        BOT.send_sticker(
            user_id, "CAACAgIAAxkBAAEG0c5jmRSpOJEV_p0KAAGAkuEQYoHmKMsAAqkWAAL5ugFI51be3L04vBAsBA")
        BOT.send_message(
            ADMIN_CHAT_ID, f'User {user_id} has been trying to get the status!')
    else:

        logs = ""
        with open(LOG_PATH) as f:
            for row in (f.readlines()[-30:]):
                logs += row + '\n'
        BOT.send_message(ADMIN_CHAT_ID, logs)


@BOT.message_handler(content_types=['text'])
def handle_text_message(message):
    user_name, user_id, text = message.chat.username, message.chat.id, message.text

    CURSOR.execute(
        f"SELECT amount_of_text_messages FROM users WHERE chat_id = ?", (user_id,))

    amount_of_text_messages_from_user = CURSOR.fetchone()[0]

    if user_id != ADMIN_CHAT_ID:
        msg = f'User {user_name}, {user_id}, {text}'
        BOT.send_message(ADMIN_CHAT_ID, msg)

    if amount_of_text_messages_from_user < 2:
        BOT.send_message(
            user_id, "No, captain... No need to write me anything.")
        CURSOR.execute(
            f"UPDATE users SET amount_of_text_messages = {amount_of_text_messages_from_user + 1} WHERE chat_id = ?", (user_id,))
        DB.commit()
    else:
        CURSOR.execute(
            f"UPDATE users SET amount_of_text_messages = 0 WHERE chat_id = ?", (user_id,))
        DB.commit()
        BOT.send_message(user_id, "Ok, i got ya.")
        BOT.send_sticker(user_id, get_random_sticker())


def get_random_image(day="wednesday"):
    path = f'images/{day}'
    images = []
    for _, _, files in os.walk(path):
        for filename in files:
            images.append(filename)
    select = randint(0, len(images)-1)
    return (f'{path}/{images[select]}')


def get_random_sticker():
    select = randint(0, len(STICKER_IDS)-1)
    return (STICKER_IDS[select])


def get_unique_image(unique_day):
    path = f'images/unique'
    unique_day_types = {}
    for _, _, files in os.walk(path):
        for filename in files:
            day_type = filename.rstrip('.jpg')
            unique_day_types[day_type] = filename

    return f'{path}/{unique_day_types[unique_day]}'


def start_mailing():
    now = datetime.now()
    current_day, current_weekday, current_month = now.day, now.weekday(), now.month
    target_hour = randint(13, 22)
    target_minutes = randint(0, len(MINUTES)-1)
    target_seconds = target_hour * 3600 + target_minutes * 60
    current_seconds = now.hour * 3600 + now.minute * 60 + now.second

    if current_seconds < target_seconds:
        waiting_time = target_seconds - current_seconds
    else:
        waiting_time = DAY_SECONDS - (current_seconds - target_seconds)

    logger.info(f"Waiting time is: {waiting_time}")
    time.sleep(waiting_time)
    logger.info("Started mailing...")

    CURSOR.execute(f"SELECT chat_id FROM users")
    users_tuples = CURSOR.fetchall()
    users = [user_id[0] for user_id in users_tuples]

    while users:
        user_id = users.pop()
        try:
            if current_weekday == 2:
                image = open(get_random_image(), 'rb')
                BOT.send_photo(user_id, image)
                logger.info(f"Sent image to: {user_id}")
            elif current_day == 15:
                image = open(get_unique_image('every_fifteen'), 'rb')
                BOT.send_photo(user_id, image)
                logger.info(f"Sent image to: {user_id}")
            elif current_month == 2:
                chance = randint(0, 100)
                if chance < 5:
                    image = open(get_unique_image('february'), 'rb')
                    BOT.send_photo(user_id, image)
                    logger.info(f"Sent image to: {user_id}")
            elif current_day == 2 and current_month == 1:
                image = open(get_unique_image('january_second'), 'rb')
                BOT.send_photo(user_id, image)
                logger.info(f"Sent image to: {user_id}")
            elif current_day == 6:
                image = open(get_unique_image('sunday'), 'rb')
                BOT.send_photo(user_id, image)
                logger.info(f"Sent image to: {user_id}")
            else:
                image = open(get_random_image("other"), 'rb')
                BOT.send_photo(user_id, image)
                logger.info(f"Sent image to: {user_id}")
        except Exception as e:
            logger.info(f"Got unexpected {e} for user {user_id}")
            users.insert(0, user_id)

    time.sleep(1)


def mailing_daemon():
    while True:
        start_mailing()


if __name__ == "__main__":
    t1 = threading.Thread(target=mailing_daemon, daemon=True)
    t1.start()
    BOT.infinity_polling()

DB.close()
