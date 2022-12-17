import threading
from utils import *
from constants import *
import handlers


if __name__ == "__main__":
    t1 = threading.Thread(target=mailing_daemon, daemon=True).start()
    BOT.infinity_polling()
