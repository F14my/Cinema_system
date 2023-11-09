import sqlite3
import os
import hashlib
import datetime
from datetime import datetime


class Auth:
    def __init__(self):
        self.name = f"customers.sqlite"

    def hash_password(self, password):
        salt = os.urandom(32)
        key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
        return salt + key

    def connect(self):
        self.con = sqlite3.connect(self.name)
        self.cur = self.con.cursor()

    def True_or_False(self, true):
        if true:
            return True
        return False

    def check_user_status(self, login):
        status = self.cur.execute(f"SELECT admin FROM users WHERE login='{login}';").fetchone()[0]
        return status

    def check_login_free(self, login):
        logins = set([str(i[0]) for i in self.cur.execute(f"SELECT login FROM users;").fetchall()])
        return self.True_or_False(len(logins & {login}) == 0)

    def check_password(self, login, password):
        self.cur.execute("SELECT password_salt, password_hash FROM users WHERE login = ?", (login,))
        stored_password_salt, stored_password_hash = self.cur.fetchone()
        key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), stored_password_salt, 100000)
        return key == stored_password_hash

    def check_user_in_system(self, login):
        logins = set([str(i[0]) for i in self.cur.execute(f"SELECT login FROM users;").fetchall()])
        return self.True_or_False(login in logins)

    def add_user(self, login, password, admin):
        password_data = self.hash_password(password)
        self.cur.execute("INSERT INTO users(login, password_salt, password_hash, admin) VALUES(?, ?, ?, ?);",
                         (login, password_data[:32], password_data[32:], admin))
        self.con.commit()

    def close(self):
        self.con.close()


class Cinema:
    def __init__(self):
        self.name = f"customers.sqlite"

    def connect(self):
        self.con = sqlite3.connect(self.name)
        self.cur = self.con.cursor()

    def add_cinema(self, cinema_name):
        self.cur.execute(f"INSERT INTO cinema(name) VALUES('{cinema_name}');")
        self.con.commit()

    def add_hall(self, cinema_name, hall_name):
        self.cur.execute(f"INSERT INTO halls(cinema_name, name) VALUES('{cinema_name}', '{hall_name}');")
        self.con.commit()

    def load_cinema_list(self):
        return set([str(i[0]) for i in self.cur.execute(f"SELECT name FROM cinema").fetchall()])

    def load_hall_list(self, cinema_name):
        que = f"SELECT name FROM halls WHERE cinema_name='{cinema_name}'"
        return set([str(i[0]) for i in self.cur.execute(que).fetchall()])

    def add_session(self, cinema, hall, date, time, film_name, duration):
        self.cur.execute(f"""INSERT INTO sessions(cinema, hall, date, time, film_name, duration) 
        VALUES('{cinema}', '{hall}', '{date}', '{time}', '{film_name}', '{duration}');""")
        self.con.commit()

    def delete_session(self, cinema, hall, date, time):
        self.cur.execute(
            f"""DELETE from sessions WHERE cinema='{cinema}' and hall= '{hall}' and date='{date}' and time='{time}'""")
        self.con.commit()

    def load_session(self, cinema, hall):
        return [list(i)[3:7] for i in self.cur.execute(f"""
        SELECT * from sessions WHERE cinema='{cinema}' and hall= '{hall}'""").fetchall()]

    def save_hall_config(self, cinema, hall, config):
        self.cur.execute(f'''UPDATE halls SET hall_config="{config}" WHERE cinema_name="{cinema}" and name="{hall}"''')
        self.con.commit()

    def save_book_config(self, cinema, hall, config):
        self.cur.execute(f'''UPDATE sessions SET seats="{config}" WHERE cinema="{cinema}" and hall="{hall}"''')
        self.con.commit()

    def update_book_config(self, cinema, hall, date, time, config):
        que = f'''UPDATE sessions SET seats="{config}" WHERE cinema="{cinema}" and hall="{hall}" 
        and date="{date}" and time="{time}"'''
        self.cur.execute(que)
        self.con.commit()

    def load_book_config(self, cinema, hall, date, time):
        que = f"""SELECT seats from sessions WHERE cinema='{cinema}' and hall= '{hall}' 
        and date='{date}' and time='{time}'"""
        return self.cur.execute(que).fetchone()[0]

    def load_hall_config(self, cinema, hall):
        try:
            hall_config = self.cur.execute(
                f'''SELECT hall_config from halls WHERE cinema_name="{cinema}" and name="{hall}"''').fetchone()[0]
            return hall_config
        except TypeError:
            return

    def load_film_list(self, cinema):
        return list([str(i[0]) for i in
                     self.cur.execute(f"""SELECT film_name FROM sessions WHERE cinema='{cinema}'""").fetchall()])

    def load_time_list(self, cinema, film, date):
        que = f"""SELECT time FROM sessions WHERE cinema='{cinema}' and film_name='{film}' and date='{date}'"""
        return list([str(i[0]) for i in self.cur.execute(que).fetchall()])

    def check_hall(self, cinema, film, time):
        return self.cur.execute(
            f"""SELECT hall FROM sessions WHERE cinema='{cinema}' and film_name='{film}' 
            and time='{time}'""").fetchone()[0]

    def delete_past_sessions(self, cinema, hall, date, time):
        que = f"""SELECT duration FROM sessions WHERE cinema='{cinema}' and date='{date}' and time='{time}'"""
        duration = self.cur.execute(que).fetchone()[0]

        if self.check_film_status(date, time, duration) == "Фильм прошёл":
            self.delete_session(cinema, hall, date, time)

    def check_film_status(self, film_date, time, duration):
        fmt = '%Y/%m/%d %H:%M:%S'
        d1 = datetime.strptime(f'{film_date} {time}', fmt)
        d2 = datetime.today()
        diff = d1 - d2
        diff_minutes = (diff.days * 24 * 60) + (diff.seconds / 60)
        if diff_minutes < 0 and abs(diff_minutes) <= duration:
            return "Фильм идёт"
        elif diff_minutes > 0:
            return "Фильм не начался"
        else:
            return "Фильм прошёл"

    def close(self):
        self.con.close()
