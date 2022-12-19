from constants import (
    ADMIN_CHAT_ID,
    GACHI_STICKER,
    POINT_LEFT,
    POINT_RIGHT,
    LOG_PATH,
)
from config import BOT, DB, logger
import utils as utils


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
        BOT.send_message(user_id, "Already registered")
        logger.info(f"Already registered user: {user_name}, chat_id - {user_id}")


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


@BOT.message_handler(content_types=["text"])
def handle_text_message(message):
    user_name, user_id, text = message.chat.username, message.chat.id, message.text

    user_messages_amount = DB.get_text_counter(user_id)

    if user_id != ADMIN_CHAT_ID:
        msg = f"User {user_name}, {user_id}, {text}"
        BOT.send_message(ADMIN_CHAT_ID, msg)

    if user_messages_amount < 2:
        BOT.send_message(user_id, "No, captain... No need to write me anything.")
        DB.increase_text_counter(user_messages_amount, user_id)
    else:
        DB.set_text_counter_to_zero(user_id)
        BOT.send_message(user_id, "Ok, i got ya.")
        BOT.send_sticker(user_id, utils.get_random_sticker())
