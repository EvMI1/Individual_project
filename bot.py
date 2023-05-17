import telebot
import sqlite3


# бот
bot = telebot.TeleBot("TOKEN")

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    print("START MESSAGE")
    bot.reply_to(message, "Привет! Я чат-бот, который поможет тебе найти университеты в России.")

# Обработчик команды /mean_score
@bot.message_handler(commands=['mean_score'])
def send_universities_by_mean_score(message):
    with sqlite3.connect('universities.db') as conn:
        cursor = conn.cursor()
        # Отправляем сообщение, запрашивающее два числа - средний балл ЕГЭ и минимальный балл поступления
        bot.send_message(message.chat.id, "Введите средний балл ЕГЭ:")
        bot.register_next_step_handler(message, get_mean_score)

def get_mean_score(message):
    # Получаем средний балл ЕГЭ от пользователя
    mean_score = message.text

    # Отправляем сообщение, запрашивающее минимальный балл поступления
    bot.send_message(message.chat.id, "Введите минимальный балл поступления:")
    bot.register_next_step_handler(message, get_min_score, mean_score)

def get_min_score(message, mean_score):
    # Получаем минимальный балл поступления от пользователя
    min_score = message.text

    # Выполняем запрос на получение всех университетов, предлагающих специальности, для которых средний балл ЕГЭ и минимальный балл поступления выше заданных значений
    with sqlite3.connect('universities.db') as conn:
        cursor = conn.cursor()
        query = "SELECT name from Universities WHERE avg_score >= ? AND min_score >= ?"
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


# Обработчик команды /specialty
@bot.message_handler(commands=['specialty'])
def send_universities_by_specialty(message):
    # Отправляем сообщение, запрашивающее название специальности
    bot.send_message(message.chat.id, "Введите название специальности:")
    bot.register_next_step_handler(message, get_specialty)

def get_specialty(message):
    # Получаем название специальности от пользователя
    specialty_name = message.text

    # Выполняем запрос на получение всех университетов, предлагающих заданную специальность
    with sqlite3.connect('universities.db') as conn:
        cursor = conn.cursor()
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



# Запускаем бота
bot.polling(none_stop=True)
