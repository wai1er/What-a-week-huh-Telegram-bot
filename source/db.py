import sqlite3


class BotDB:
    def __init__(self, db_file, same_thread):
        self.conn = sqlite3.connect(db_file, check_same_thread=same_thread)
        self.cursor = self.conn.cursor()

    def register_user(self, user_name, user_id):
        self.cursor.execute(
            f"INSERT INTO users VALUES (?, ?, ?, ?, ?, ?);",
            (user_name, user_id, 0, False, 0, 0),
        )
        return self.conn.commit()

    def delete_user(self, user_id):
        self.cursor.execute(f"DELETE FROM users WHERE chat_id = ?", (user_id,))
        return self.conn.commit()

    def set_user_blocked_bot(self, user_id):
        self.cursor.execute(
            f"UPDATE users SET has_blocked = 1 WHERE chat_id = ?",
            (user_id,),
        )
        return self.conn.commit()

    def set_user_unblocked_bot(self, user_id):
        self.cursor.execute(
            f"UPDATE users SET has_blocked = 0 WHERE chat_id = ?",
            (user_id,),
        )
        return self.conn.commit()

    def get_non_blocked_users(self):
        chat_id_tuples = self.cursor.execute(
            "SELECT chat_id FROM users WHERE has_blocked <> 1"
        )
        chat_ids = [chat_id[0] for chat_id in chat_id_tuples]
        return chat_ids

    def has_user_blocked(self, user_id):
        has_blocked = self.cursor.execute(
            f"SELECT has_blocked FROM users WHERE chat_id = ?", (user_id,)
        ).fetchone()[0]
        return has_blocked

    def increase_user_points(self, user_id):
        self.cursor.execute(
            f"UPDATE users SET user_points = bot_points + 1 WHERE chat_id = ?",
            (user_id,),
        )
        return self.conn.commit()

    def increase_bot_points(self, user_id):
        self.cursor.execute(
            f"UPDATE users SET bot_points = bot_points + 1 WHERE chat_id = ?",
            (user_id,),
        )
        return self.conn.commit()

    def get_users_chat_id(self):
        chat_id_tuples = self.cursor.execute("SELECT chat_id FROM users")
        chat_ids = [chat_id[0] for chat_id in chat_id_tuples]
        return chat_ids

    def get_text_counter(self, user_id):
        counter = self.cursor.execute(
            f"SELECT text_messages_counter FROM users WHERE chat_id = ?", (user_id,)
        )
        return counter.fetchone()[0]

    def get_user_gamestats(self, user_id):
        stats = self.cursor.execute(
            f"SELECT bot_points, user_points FROM users WHERE chat_id = ?", (user_id,)
        )
        bot_points, user_points = stats.fetchone()

        return bot_points, user_points

    def increase_text_counter(self, user_id):
        self.cursor.execute(
            f"UPDATE users SET text_messages_counter =  text_messages_counter + 1 WHERE chat_id = ?",
            (user_id,),
        )
        return self.conn.commit()

    def set_text_counter_to_zero(self, user_id):
        self.cursor.execute(
            f"UPDATE users SET text_messages_counter = 0 WHERE chat_id = ?",
            (user_id,),
        )
        return self.conn.commit()

    def close(self):
        self.conn.close()
