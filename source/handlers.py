from constants import (
    ADMIN_CHAT_ID,
    GACHI_STICKER,
    POINT_LEFT,
    POINT_RIGHT,
    LOG_PATH,
    GAME_TYPES,
)
from config import BOT, DB, logger
from telebot import types
import utils as utils

__commands__ = ["/start", "/game", "/gamestats", "/status", "/when", "/commands"]


@BOT.message_handler(commands=["start"])
def handle_start_command(message):
    user_name, user_id = message.chat.username, message.chat.id

    chat_ids = DB.get_users_chat_id()

    if user_id not in chat_ids:
        if user_name != None:
            DB.register_user(user_name, user_id)
            BOT.send_message(user_id, f"Hello, captain {user_name}...")
            logger.info(f"New registered user: {user_name}, chat_id - {user_id}")
        else:
            DB.register_user(str(user_id), user_id)
            BOT.send_message(user_id, f"Hello, stranger {POINT_RIGHT}{POINT_LEFT}...")
            logger.info(f"New registered user: {user_id}, chat_id - {user_id}")
    else:
        has_blocked = DB.has_user_blocked(user_id)
        if has_blocked:
            DB.set_user_unblocked_bot(user_id)
            BOT.send_message(user_id, f"Welcome back, captain {user_name}...")
            logger.info(f"User {user_name} unblocked the bot, chat_id - {user_id}")
        else:
            BOT.send_message(user_id, "Already registered")
            logger.info(f"Already registered user: {user_name}, chat_id - {user_id}")


@BOT.message_handler(commands=["game"])
def handle_game_command(message):
    user_id = message.chat.id
    games = "\n".join(GAME_TYPES)
    BOT.send_message(
        user_id,
        f"You can send me a dice so we can play. \n Possible types of game: \n{games}. \n You can also check current stats with /gamestats command",
    )


@BOT.message_handler(commands=["gamestats"])
def handle_gamestats_command(message):
    user_id = message.chat.id
    bot_points, user_points = DB.get_user_gamestats(user_id)
    BOT.send_message(
        user_id, f"Currents stats are: Me: {bot_points}, Captain: {user_points}."
    )


@BOT.message_handler(commands=["status"])
def handle_status_command(message):
    user_id = message.chat.id
    if user_id != ADMIN_CHAT_ID:
        BOT.send_message(user_id, "No, captain. You've entered the wrong door.")
        BOT.send_sticker(
            user_id,
            GACHI_STICKER,
        )
        BOT.send_message(
            ADMIN_CHAT_ID, f"User {user_id} has been trying to get the status!"
        )
    else:

        logs = utils.get_logs(LOG_PATH)
        BOT.send_message(user_id, logs)


@BOT.message_handler(commands=["when"])
def handle_when_command(message):
    time_to_wait = utils.time_till_meme()
    user_id = message.chat.id
    if not time_to_wait:
        msg = f"Wait for next day to get your meme"
        BOT.send_message(user_id, msg)
    else:
        msg = f"I'll send you meme in {time_to_wait}"
        BOT.send_message(user_id, msg)


@BOT.message_handler(commands=["commands"])
def handle_game_command(message):
    user_id = message.chat.id
    commands = "\n".join(__commands__)
    BOT.send_message(user_id, f"Current commands are: \n{commands}")


@BOT.message_handler(content_types=["text"])
def handle_text_message(message):
    user_name, user_id, text = message.chat.username, message.chat.id, message.text
    user_messages_amount = DB.get_text_counter(user_id)

    if user_messages_amount < 2:
        BOT.send_message(user_id, "No, captain... No need to write me anything.")
        DB.increase_text_counter(user_id)
    else:
        DB.set_text_counter_to_zero(user_id)
        BOT.send_message(user_id, "Ok, i got ya.")
        BOT.send_sticker(user_id, utils.get_random_sticker())


@BOT.message_handler(content_types=["dice"])
def handle_sticker_message(message):
    user_id = message.chat.id
    utils.roll_a_dice(user_id, message)
