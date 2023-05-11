import telebot
import sqlite3

from BD_Universities import conn


# Создание соединения с базой данных
def create_connection():
    conn = sqlite3.connect('universities.db')
    return conn

# бот
bot = telebot.TeleBot("6106236845:AAF6MbKbhbEI6zck0El334zJzhTUAtIsgZw")

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Я чат-бот, который поможет тебе найти университеты в России.")

# Обработчик команды /mean_score
@bot.message_handler(commands=['mean_score'])
def send_universities_by_mean_score(message):
    conn = create_connection()
    cursor = conn.cursor()

    # Отправляем сообщение, запрашивающее два числа - средний балл ЕГЭ и минимальный балл поступления
    bot.send_message(message.chat.id, "Введите средний балл ЕГЭ:")
    bot.register_next_step_handler(message, get_mean_score, cursor)

def get_mean_score(message, cursor):
    # Получаем средний балл ЕГЭ от пользователя
    mean_score = message.text

    # Отправляем сообщение, запрашивающее минимальный балл поступления
    bot.send_message(message.chat.id, "Введите минимальный балл поступления:")
    bot.register_next_step_handler(message, get_min_score, cursor, mean_score)

def get_min_score(message, cursor, mean_score):
    # Получаем минимальный балл поступления от пользователя
    min_score = message.text

    # Выполняем запрос на получение всех университетов, предлагающих специальности, для которых средний балл ЕГЭ и минимальный балл поступления выше заданных значений
    query = "SELECT name from Universities WHERE avg_score >= ? AND admissions_score >= ?"
    cursor.execute(query, (mean_score, min_score,))
    universities = cursor.fetchall()

    # Отправляем пользователю список университетов
    if len(universities) > 0:
        response = "Список университетов, предлагающих специальности с средним баллом ЕГЭ выше " + str(mean_score) + " и минимальным баллом поступления выше " + str(min_score) + ":\n"
        for university in universities:
            response += university[0] + "\n"
    else:
        response = "По вашему запросу ничего не найдено"

    bot.send_message(message.chat.id, response)

    # Закрываем соединение с БД
    cursor.close()
    conn.close()

# Обработчик команды /specialty
@bot.message_handler(commands=['specialty'])
def send_universities_by_specialty(message):
    conn = create_connection()
    cursor = conn.cursor()

    # Отправляем сообщение, запрашивающее название специальности
    bot.send_message(message.chat.id, "Введите название специальности:")
    bot.register_next_step_handler(message, get_specialty, cursor)

def get_specialty(message, cursor):
    # Получаем название специальности от пользователя
    specialty_name = message.text

    # Выполняем запрос на получение всех университетов, предлагающих заданную специальность
    query = "SELECT name from Universities WHERE specialties like ?"
    cursor.execute(query, ('%' + specialty_name + '%',))
    universities = cursor.fetchall()

    # Отправляем пользователю список университетов
    if len(universities) > 0:
        response = "Список университетов, предлагающих специальность " + specialty_name + ":\n"
        for university in universities:
            response += university[0] + "\n"
    else:
        response = "По вашему запросу ничего не найдено"

    bot.send_message(message.chat.id, response)

    # Закрываем соединение с БД
    cursor.close()
    conn.close()

# Запускаем бота
bot.polling(none_stop=True)