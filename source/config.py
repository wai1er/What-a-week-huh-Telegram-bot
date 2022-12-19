import telebot
import logging
from db import BotDB
from constants import TOKEN, LOG_PATH


BOT = telebot.TeleBot(TOKEN)
DB = BotDB("users.db", False)

logger = telebot.logger
telebot.logger.setLevel(logging.INFO)
logging.basicConfig(
    filename=LOG_PATH,
    level=logging.INFO,
    format=" %(asctime)s - %(levelname)s - %(message)s",
)
