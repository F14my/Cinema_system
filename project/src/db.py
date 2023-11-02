import sqlite3
import os


class Auth:
    def __init__(self):
        self.path = os.getcwd()
        self.path = self.path.replace("\\", "/")
        self.name = f"{self.path}/db/customers.sqlite"

    def connect(self):
        self.con = sqlite3.connect(self.name)
        self.cur = self.con.cursor()

    def True_or_False(self, true):
        if true:
            return True
        return False

    def check_login_free(self, login):
        logins = set([str(i[0]) for i in self.cur.execute(f"SELECT login FROM users;").fetchall()])
        return self.True_or_False(len(logins & {login}) == 0)

    def check_password(self, login, password):
        password_in_db = self.cur.execute(f"SELECT password FROM users WHERE login='{login}';").fetchone()[0]
        return self.True_or_False(password_in_db == password)

    def check_user_in_system(self, login):
        logins = set([str(i[0]) for i in self.cur.execute(f"SELECT login FROM users;").fetchall()])
        return self.True_or_False(login in logins)

    def add_user(self, login, password, admin):
        self.cur.execute(f"INSERT INTO users(login, password, admin) VALUES('{login}', '{password}', '{admin}');")
        self.con.commit()

    def close(self):
        self.con.close()


class Cinema:
    def __init__(self):
        self.path = os.getcwd()
        self.path = self.path.replace("\\", "/")
        self.name = f"{self.path}/db/customers.sqlite"

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


    def close(self):
        self.con.close()
