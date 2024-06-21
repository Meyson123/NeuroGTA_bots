import sqlite3 as sql
import asyncio

# Создаем таблицу Users_activity (Нужна только 1 раз)
def create_db():
    cursor, con = open_db()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Users_activity (
    username TEXT NOT NULL,
    count INTEGER
    )
    ''')
    close_db(con)


# Устанавливаем соединение с базой данных
def open_db():
    con = sql.connect('SQL/my_database.db')
    cursor = con.cursor()
    return cursor, con


def close_db(con):
    con.commit()
    con.close()


# Создание нового пользователя
def new_user(username):
    cursor, con = open_db()
    cursor.execute('INSERT INTO Users_activity (username,count) VALUES (?,?) ', (username, 0))
    close_db(con)


# Увелечение счета пользователя (на 1)
def add_count(username):
    cursor, con = open_db()
    cursor.execute('SELECT count FROM Users_activity WHERE username = ?', (username,))
    count = cursor.fetchone()[0]
    cursor.execute('UPDATE Users_activity SET count = ? WHERE username = ?', (count + 1, username))
    close_db(con)


# Удаление пользователя
def remove_user(username):
    cursor, con = open_db()
    cursor.execute('DELETE FROM Users_activity WHERE username = ?', (username,))
    close_db(con)


# Список всех пользователей и их активность
def show_list():
    cursor, con = open_db()
    users_list = []
    cursor.execute('SELECT * FROM Users_activity')
    users = cursor.fetchall()
    for user in users:
        user_dict = {
            'Имя': user[0],
            'Количество запросов': user[1]
        }
        users_list.append(user_dict)
    close_db(con)
    return users_list


async def search_nick(nickname):
    cursor, con = open_db()
    users = ()
    cursor.execute('SELECT username FROM Users_activity ')
    username_list = cursor.fetchall()
    for i in username_list:
        users += tuple(i)
    print(users)
    if nickname in users:
        pass
    else: new_user(nickname)
    close_db(con)
