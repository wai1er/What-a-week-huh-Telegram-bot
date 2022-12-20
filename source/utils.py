import os
import time
from random import randint, choice
from datetime import datetime
from constants import (
    STICKER_IDS,
    DAY_SECONDS,
    MINUTES,
    BLOCKED_USER_ERROR_CODE,
)
from config import DB, BOT, logger
from telebot.apihelper import ApiTelegramException


def get_random_sticker():
    sticker_id = choice(STICKER_IDS)
    return sticker_id


def time_formatter(time):
    if time < 10:
        return "0" + str(time)
    else:
        return time


def get_images(day):
    path = f"../images/{day}"
    day_types = {}
    for _, _, files in os.walk(path):
        for filename in files:
            day_type = filename[:-4]
            day_types[day_type] = filename

    return day_types


def get_random_image(day="wednesday"):
    path = f"../images/{day}"
    images = get_images(day)
    random_image = choice(list(images.values()))
    return f"{path}/{random_image}"


def get_unique_image(unique_day):
    day = "unique"
    path = f"../images/{day}"
    unique_day_types = get_images(day)

    return f"{path}/{unique_day_types[unique_day]}"


def get_current_seconds():
    now = datetime.now()
    current_seconds = now.hour * 3600 + now.minute * 60 + now.second

    return current_seconds


def time_till_meme():
    current_seconds = get_current_seconds()
    target_seconds = get_target_time()

    if current_seconds < target_seconds:
        current_waiting_time = target_seconds - current_seconds
    else:
        return 0

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


def get_target_time():
    now = datetime.now()
    if now.strftime("%A") == "Monday":
        target_hour = randint(7, 10)
        target_minutes = randint(0, len(MINUTES) - 1)
        target_seconds = target_hour * 3600 + target_minutes * 60
    else:
        target_hour = randint(10, 20)
        target_minutes = randint(0, len(MINUTES) - 1)
        target_seconds = target_hour * 3600 + target_minutes * 60

    return target_seconds


def get_waiting_time(target_seconds):
    current_seconds = get_current_seconds()

    if current_seconds < target_seconds:
        waiting_time = target_seconds - current_seconds
    else:
        waiting_time = DAY_SECONDS - (current_seconds - target_seconds)

    return waiting_time


def get_time_till_next_day(waiting_time):
    current_seconds = get_current_seconds()
    time_till_next_day = DAY_SECONDS - current_seconds - waiting_time

    return time_till_next_day


def mailing(user_id):
    now = datetime.now()
    current_day, current_weekday, current_month, current_date = (
        now.day,
        now.strftime("%A"),
        now.strftime("%B"),
        now.strftime("%D")[:-3],
    )
    if current_date == "01/02":
        image = open(get_unique_image("january_second"), "rb")
        BOT.send_photo(user_id, image)
        logger.info(f"Sent image to: {user_id}")
    elif current_day == 15:
        image = open(get_unique_image("every_fifteen"), "rb")
        BOT.send_photo(user_id, image)
        logger.info(f"Sent image to: {user_id}")
    elif current_month == "February":
        chance = randint(0, 100)
        if chance < 5:
            image = open(get_unique_image("february"), "rb")
            BOT.send_photo(user_id, image)
            logger.info(f"Sent image to: {user_id}")
    elif current_weekday == "Sunday":
        image = open(get_unique_image("sunday"), "rb")
        BOT.send_photo(user_id, image)
        logger.info(f"Sent image to: {user_id}")
    elif current_weekday == "Wednesday":
        image = open(get_random_image(current_weekday), "rb")
        BOT.send_photo(user_id, image)
        logger.info(f"Sent image to: {user_id}")
    else:
        image = open(get_random_image("other"), "rb")
        BOT.send_photo(user_id, image)
        logger.info(f"Sent image to: {user_id}")


def start_mailing():
    target_time = get_target_time()
    waiting_time = get_waiting_time(target_time)
    time_till_next_day = get_time_till_next_day(waiting_time)

    logger.info(f"Waiting time is: {time_till_meme()}, {waiting_time}")
    time.sleep(waiting_time)
    logger.info("Started mailing...")

    users = DB.get_users_chat_id()

    while users:
        user_id = users.pop()
        # change the block of user to flag in database
        try:
            mailing(user_id)
        except ApiTelegramException as e:
            if e.error_code == BLOCKED_USER_ERROR_CODE:
                DB.delete_user(user_id)
                logger.info(
                    f"User {user_id} blocked the bot and has been deleted from the database."
                )
            logger.info(f"Got unexpected {e} for user {user_id} skipping him")

    # create config file here
    logger.info(f"Waiting for next day to choose the time: {time_till_next_day}")
    time.sleep(time_till_next_day)


def mailing_daemon():
    while True:
        start_mailing()