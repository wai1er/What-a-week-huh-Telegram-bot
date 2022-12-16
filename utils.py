import os
from random import randint
from constants import *


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


def get_random_sticker():
    select = randint(0, len(STICKER_IDS) - 1)
    return STICKER_IDS[select]


def get_unique_image(unique_day):
    path = f"images/unique"
    unique_day_types = {}
    for _, _, files in os.walk(path):
        for filename in files:
            day_type = filename.rstrip(".jpg")
            unique_day_types[day_type] = filename

    return f"{path}/{unique_day_types[unique_day]}"
