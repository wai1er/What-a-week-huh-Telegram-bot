import sqlite3


class BotDB:
    def __init__(self, db_file, same_thread):
        self.conn = sqlite3.connect(db_file, check_same_thread=same_thread)
        self.cursor = self.conn.cursor()

    def register_user(self, user_name, user_id):
        self.cursor.execute(
            f"INSERT INTO users VALUES (?, ?, ?);", (user_name, user_id, 0)
        )
        return self.conn.commit()

    def delete_user(self, user_id):
        self.cursor.execute(f"DELETE FROM users WHERE chat_id = ?", (user_id,))
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

    def increase_text_counter(self, counter, user_id):
        self.cursor.execute(
            f"UPDATE users SET text_messages_counter = {counter + 1} WHERE chat_id = ?",
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
