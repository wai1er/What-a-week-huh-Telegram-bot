import os
import time
from random import randint
from datetime import datetime
from constants import *
from config import *
from telebot.apihelper import ApiTelegramException


def get_random_sticker():
    select = randint(0, len(STICKER_IDS) - 1)
    return STICKER_IDS[select]


def time_formatter(time):
    if time < 10:
        return "0" + str(time)
    else:
        return time


def get_random_image(day="wednesday"):
    path = f"images/{day}"
    images = []
    for _, _, files in os.walk(path):
        for filename in files:
            images.append(filename)
    select = randint(0, len(images) - 1)
    return f"{path}/{images[select]}"


def get_unique_image(unique_day):
    path = f"images/unique"
    unique_day_types = {}
    for _, _, files in os.walk(path):
        for filename in files:
            day_type = filename.rstrip(".jpg")
            unique_day_types[day_type] = filename

    return f"{path}/{unique_day_types[unique_day]}"


def time_till_meme():
    global TARGET_SECONDS

    if TARGET_SECONDS == 0:
        return 0

    now = datetime.now()
    current_seconds = now.hour * 3600 + now.minute * 60 + now.second

    if current_seconds < TARGET_SECONDS:
        current_waiting_time = TARGET_SECONDS - current_seconds
    else:
        current_waiting_time = DAY_SECONDS - (current_seconds - TARGET_SECONDS)

    seconds = current_waiting_time % (24 * 3600)
    hours = time_formatter(seconds // 3600)
    seconds %= 3600
    minutes = time_formatter(seconds // 60)
    seconds = time_formatter(seconds % 60)
    return f"{hours}:{minutes}:{seconds}."


def get_logs(log_path):
    logs = ""
    with open(log_path) as f:
        for row in f.readlines()[-30:]:
            logs += row + "\n"
    return logs


def start_mailing():
    global TARGET_SECONDS
    now = datetime.now()
    current_day, current_weekday, current_month = now.day, now.weekday(), now.month
    target_hour = randint(13, 22)
    target_minutes = randint(0, len(MINUTES) - 1)
    TARGET_SECONDS = target_hour * 3600 + target_minutes * 60
    current_seconds = now.hour * 3600 + now.minute * 60 + now.second

    if current_seconds < TARGET_SECONDS:
        waiting_time = TARGET_SECONDS - current_seconds
    else:
        waiting_time = DAY_SECONDS - (current_seconds - TARGET_SECONDS)

    time_till_next_day = DAY_SECONDS - current_seconds - waiting_time

    logger.info(f"Waiting time is: {time_till_meme()}, {waiting_time}")
    time.sleep(waiting_time)
    logger.info("Started mailing...")

    users = DB.get_users_chat_id()

    while users:
        user_id = users.pop()
        try:
            if current_weekday == 2:
                image = open(get_random_image(), "rb")
                BOT.send_photo(user_id, image)
                logger.info(f"Sent image to: {user_id}")
            elif current_day == 15:
                image = open(get_unique_image("every_fifteen"), "rb")
                BOT.send_photo(user_id, image)
                logger.info(f"Sent image to: {user_id}")
            elif current_month == 2:
                chance = randint(0, 100)
                if chance < 5:
                    image = open(get_unique_image("february"), "rb")
                    BOT.send_photo(user_id, image)
                    logger.info(f"Sent image to: {user_id}")
            elif current_day == 2 and current_month == 1:
                image = open(get_unique_image("january_second"), "rb")
                BOT.send_photo(user_id, image)
                logger.info(f"Sent image to: {user_id}")
            elif current_weekday == 6:
                image = open(get_unique_image("sunday"), "rb")
                BOT.send_photo(user_id, image)
                logger.info(f"Sent image to: {user_id}")
            else:
                image = open(get_random_image("other"), "rb")
                BOT.send_photo(user_id, image)
                logger.info(f"Sent image to: {user_id}")
        except ApiTelegramException as e:
            if e.error_code == BLOCKED_USER_ERROR_CODE:
                DB.delete_user(user_id)
                logger.info(
                    f"User {user_id} blocked the bot and has been deleted from the database."
                )
            logger.info(f"Got unexpected {e} for user {user_id} skipping him")

    TARGET_SECONDS = 0
    logger.info(f"Waiting for next day to choose the time: {time_till_next_day}")
    time.sleep(time_till_next_day)


def mailing_daemon():
    while True:
        start_mailing()
