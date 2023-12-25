import sqlite3

import telebot
from telebot import types

# бот
bot = telebot.TeleBot("6106236845:AAF6MbKbhbEI6zck0El334zJzhTUAtIsgZw")


# Обработчик команды /start
@bot.message_handler(commands=["start"])
def send_welcome(message):
    print("START MESSAGE")
    bot.reply_to(
        message,
        "Привет! Я чат-бот, который поможет тебе найти университеты в России, предлагающие"
        " преимущесвтенно технические специальности. Ты можешь обратиться за  помощью командой /help",
    )


# Обработчик команды /help
@bot.message_handler(commands=["help"])
def handle_help_command(message):
    response = (
        "Доступные команды:\n\n"
        "/universities - Введите название университета. Бот отправит Вам информацию о нем.\n\n"
        "/specialty - Введите название специальности. Бот отправит Вам список"
        " университетов, в которых присутствуют интересующие Вас специальности.\n\n"
        "/mean_score - Введите свой средний балл за ЕГЭ и минимальный балл за экзамен."
        " Бот выведет список университетов."
    )

    bot.send_message(message.chat.id, response)


# Обработчик команды /mean_score
@bot.message_handler(commands=["mean_score"])
def send_universities_by_mean_score(message):
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
    with sqlite3.connect("universities.db") as conn:
        cursor = conn.cursor()
        query = "SELECT name from Universities WHERE avg_score <= ? AND min_score >= ?"
        cursor.execute(
            query,
            (
                mean_score,
                min_score,
            ),
        )
        universities = cursor.fetchall()

    # Отправляем пользователю список университетов
    if len(universities) > 0:
        response = (
            "Список университетов, предлагающих специальности с средним баллом ЕГЭ ниже "
            + str(mean_score)
            + " и минимальным баллом поступления выше "
            + str(min_score)
            + ":\n"
        )
        for university in universities:
            response += university[0] + "\n"
    else:
        response = "По вашему запросу ничего не найдено"

    bot.send_message(message.chat.id, response)


# Глобальная переменная для хранения текущей клавиатуры пользователя
user_keyboards = {}


@bot.message_handler(commands=["specialty"])
def send_universities_by_specialty(message):
    # Создаем клавиатуру с кнопками специальностей
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    specialties = [
        "Прикладная математика",
        "Радиотехника",
        "Программирование",
        "Информационная безопасность",
        "Фундаментальная информатика и компьютерные науки",
        "Информационные системы и технологии",
        "Педагогическое образование",
        "Бизнес-информатика",
        "Инфокоммуникационные технологии и системы связи",
        "Информационная безопасность автоматизированных систем",
        "Информационные системы и технологии",
        "Компьютерная безопасность",
        "Механика и математическое моделирование",
        "Информатика и вычислительная техника",
        "Математическое обеспечение и администрирование информационных систем",
        "Лазерная техника и лазерные технологии",
    ]
    for specialty in specialties:
        markup.add(types.KeyboardButton(text=specialty))

    # Сохраняем текущую клавиатуру пользователя
    user_keyboards[message.chat.id] = markup

    # Отправляем сообщение с клавиатурой
    bot.send_message(
        message.chat.id, "Выберите специальность из списка:", reply_markup=markup
    )

    # Регистрируем обработчик выбора специальности
    bot.register_next_step_handler(message, get_specialty)


@bot.message_handler(commands=["cancel"])
def cancel_command(message):
    # Отменяем текущую операцию и скрываем клавиатуру
    bot.send_message(
        message.chat.id, "Операция отменена.", reply_markup=types.ReplyKeyboardRemove()
    )
    # Очищаем текущую клавиатуру пользователя
    user_keyboards.pop(message.chat.id, None)


def get_specialty(message):
    # Получаем выбранную специальность от пользователя
    specialty_name = message.text.lower()

    # Выполняем запрос на получение всех университетов, предлагающих заданную специальность
    with sqlite3.connect("universities.db") as conn:
        cursor = conn.cursor()
        query = (
            f"SELECT name FROM Universities WHERE specialties LIKE '%{specialty_name}%'"
        )
        cursor.execute(query)
        universities = cursor.fetchall()

    # Создаем клавиатуру с кнопками университетов
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for university in universities:
        markup.add(types.KeyboardButton(text=university[0]))

    # Сохраняем текущую клавиатуру пользователя
    user_keyboards[message.chat.id] = markup

    # Отправляем сообщение с клавиатурой
    bot.send_message(
        message.chat.id, "Выберите университет из списка:", reply_markup=markup
    )

    # Регистрируем обработчик выбора университета
    bot.register_next_step_handler(message, get_university_info)


def get_university_info(message):
    # Получаем выбранный университет от пользователя
    selected_university = message.text

    # Ищем университет в БД по названию
    with sqlite3.connect("universities.db") as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM Universities WHERE name LIKE ?",
            ("%" + selected_university + "%",),
        )
        result = cursor.fetchone()

    # Если университет найден, отправляем информацию
    if result:
        response = (
            f"Университет: {result[1]}\n\n"
            f"Специальности: {result[2]}\n"
            f"Минимальный балл: {result[3]}\n"
            f"Средний балл: {result[4]}\n"
            f"Продолжительность обучения: {result[5]}\n"
            f"Адрес: {result[6]}\n"
            f"Контакт: {result[7]}\n"
            f"Общежитие: {result[8]}\n"
            f"Веб-сайт: {result[9]}"
        )
    else:
        response = "Информация об университете не найдена."

    bot.send_message(
        message.chat.id, response, reply_markup=types.ReplyKeyboardRemove()
    )

    # Очищаем текущую клавиатуру пользователя
    user_keyboards.pop(message.chat.id, None)


# Обработчик команды /universities
@bot.message_handler(commands=["universities"])
def handle_universities_command(message):
    bot.send_message(message.chat.id, "Введите название университета:")


# Обработчик текстовых сообщений
@bot.message_handler(func=lambda message: True)
def handle_text_message(message):
    # Получаем название университета из сообщения пользователя
    university_name = message.text

    # Ищем университет в БД по названию
    with sqlite3.connect("universities.db") as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM Universities WHERE name LIKE ?",
            ("%" + university_name + "%",),
        )
        result = cursor.fetchone()

    # Если университет найден, отправляем информацию
    if result:
        response = (
            f"Университет: {result[1]}\n\n"
            f"Специальности: {result[2]}\n"
            f"Минимальный балл: {result[3]}\n"
            f"Средний балл: {result[4]}\n"
            f"Продолжительность обучения: {result[5]}\n"
            f"Адрес: {result[6]}\n"
            f"Контакт: {result[7]}\n"
            f"Общежитие: {result[8]}\n"
            f"Веб-сайт: {result[9]}"
        )

    # Если университет не найден, отправляем сообщение об ошибке
    else:
        response = "Университет не найден. Попробуйте ввести другое название."

    bot.send_message(message.chat.id, response)


# Запускаем бота
bot.infinity_polling()
