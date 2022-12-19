import threading
from utils import mailing_daemon
from config import BOT
import handlers as handlers


if __name__ == "__main__":
    t1 = threading.Thread(target=mailing_daemon, daemon=True).start()
    BOT.infinity_polling()
