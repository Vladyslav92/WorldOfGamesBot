import json
import re
from datetime import datetime
from telebot import types

GAMES_PATH = "base/games.json"
user_sessions = {}


def create_game(bot, message):
    chat_id = message.chat.id
    user_sessions[chat_id] = {}
    bot.send_message(chat_id, "🔎 Введите название игры для поиска (например Алкотестер):")
    bot.register_next_step_handler(message, lambda msg: get_game_name(bot, msg))


def get_game_name(bot, message):
    chat_id = message.chat.id
    game_name = message.text.strip()

    try:
        with open(GAMES_PATH, "r", encoding="utf-8") as f:
            games = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        games = []

    if game_name in games:
        bot.send_message(chat_id, "❌ Такая игра уже существует. Попробуйте другое название:")
        bot.register_next_step_handler(message, lambda msg: get_game_name(bot, msg))
        return

    user_sessions[chat_id]["game_name"] = game_name
    bot.send_message(chat_id, "🎲 Введите длительность обучения (например 30м, 1ч, 1ч 30м):")
    bot.register_next_step_handler(message, lambda msg: get_duration(bot, msg, "training"))


def get_duration(bot, message, key):
    chat_id = message.chat.id
    text = message.text.strip()
    pattern = r'^((\d{1,2}ч)?\s?(\d{1,2}м)?)$'
    match = re.match(pattern, text)

    if not match:
        bot.send_message(chat_id, "❌ Неверный формат. Примеры: '30м', '1ч', '1ч 30м'")
        bot.register_next_step_handler(message, lambda msg: get_duration(bot, msg, key))
        return

    if "ч" in text:
        hours = int(re.search(r'(\d{1,2})ч', text).group(1))
        if not (1 <= hours <= 24):
            bot.send_message(chat_id, "❌ Часы должны быть от 1 до 24.")
            bot.register_next_step_handler(message, lambda msg: get_duration(bot, msg, key))
            return

    if "м" in text:
        minutes = int(re.search(r'(\d{1,2})м', text).group(1))
        if not (1 <= minutes <= 60):
            bot.send_message(chat_id, "❌ Минуты должны быть от 1 до 60.")
            bot.register_next_step_handler(message, lambda msg: get_duration(bot, msg, key))
            return

    user_sessions[chat_id][key] = text
    if key == "training":
        bot.send_message(chat_id, "🎲 Введите длительность партии (например 30м, 1ч, 1ч 30м):")
        bot.register_next_step_handler(message, lambda msg: get_duration(bot, msg, "party"))
    else:
        bot.send_message(chat_id, "🎲 Выберите день (Введите дату начала в формате дд.мм.гггг):")
        bot.register_next_step_handler(message, lambda msg: get_date(bot, msg))


def get_date(bot, message):
    chat_id = message.chat.id
    text = message.text.strip()
    try:
        date_obj = datetime.strptime(text, "%d.%m.%Y")
        user_sessions[chat_id]["date"] = date_obj
        bot.send_message(chat_id, "🎲 Выберите время (например 14:00):")
        bot.register_next_step_handler(message, lambda msg: get_time(bot, msg))
    except ValueError:
        bot.send_message(chat_id, "❌ Неверный формат. Введите дату в формате дд.мм.гггг")
        bot.register_next_step_handler(message, lambda msg: get_date(bot, msg))


def get_time(bot, message):
    chat_id = message.chat.id
    text = message.text.strip()
    try:
        time_obj = datetime.strptime(text, "%H:%M").time()
        user_sessions[chat_id]["time"] = time_obj
        bot.send_message(chat_id, "👥 Введите количество игроков:")
        bot.register_next_step_handler(message, lambda msg: get_number(bot, msg, "players"))
    except ValueError:
        bot.send_message(chat_id, "❌ Неверный формат. Введите время в формате ЧЧ:ММ")
        bot.register_next_step_handler(message, lambda msg: get_time(bot, msg))


def get_number(bot, message, key):
    chat_id = message.chat.id
    text = message.text.strip()

    if not text.isdigit():
        bot.send_message(chat_id, "❌ Введите число.")
        bot.register_next_step_handler(message, lambda msg: get_number(bot, msg, key))
        return

    user_sessions[chat_id][key] = int(text)

    if key == "players":
        bot.send_message(chat_id, "👥 Введите количество резервных мест:")
        bot.register_next_step_handler(message, lambda msg: get_number(bot, msg, "reserve"))
    else:
        # Показываем inline-кнопку "Пропустить"
        markup = types.InlineKeyboardMarkup()
        skip_button = types.InlineKeyboardButton("💳 Пропустить", callback_data="skip_comment")
        markup.add(skip_button)

        bot.send_message(chat_id, "🎲 Введите свой комментарий:", reply_markup=markup)

        # Регистрируем обработку текстового комментария
        bot.register_next_step_handler(message, lambda msg: handle_text_comment(bot, msg))


def handle_text_comment(bot, message):
    chat_id = message.chat.id
    comment = message.text.strip()

    # Проверяем, что пользователь не нажал кнопку "Пропустить"
    if comment != "💳 Пропустить":
        user_sessions[chat_id]["comment"] = comment
        show_summary(bot, chat_id)


def get_comment(bot, message):
    chat_id = message.chat.id
    comment = "" if message.text == "💳 Пропустить" else message.text.strip()
    user_sessions[chat_id]["comment"] = comment
    show_summary(bot, chat_id)


def show_summary(bot, chat_id):
    data = user_sessions[chat_id]
    date_obj = data["date"]
    weekday = date_obj.strftime("%A")

    # Перевод дня недели
    weekday_ru = {
        "Monday": "Понедельник", "Tuesday": "Вторник", "Wednesday": "Среда",
        "Thursday": "Четверг", "Friday": "Пятница", "Saturday": "Суббота", "Sunday": "Воскресенье"
    }

    # Перевод месяца
    months_ru = {
        "January": "января", "February": "февраля", "March": "марта",
        "April": "апреля", "May": "мая", "June": "июня",
        "July": "июля", "August": "августа", "September": "сентября",
        "October": "октября", "November": "ноября", "December": "декабря"
    }

    date_str = date_obj.strftime("%d %B %Y")
    for en, ru in months_ru.items():
        date_str = date_str.replace(en, ru)

    summary = (
        f"🎲 {data['game_name']}\n\n"
        f"🗓 {date_str}\n"
        f"🗓 {weekday_ru.get(weekday, weekday)}\n"
        f"🕓 {data['time'].strftime('%H:%M')}\n\n"
        f"👤 Игроков: {data['players']}\n"
        f"👤 Резервных мест: {data['reserve']}\n\n"
        f"🕓 Обучение: {data['training']}\n"
        f"🕓 Время партии: {data['party']}\n\n"
        f"{data['comment'] if data['comment'] else ''}"
    )

    bot.send_message(chat_id, summary)

    # Кнопки "Опубликовать" и "Отмена"
    markup = types.InlineKeyboardMarkup()
    publish_btn = types.InlineKeyboardButton("✅ Опубликовать", callback_data="publish_game")
    cancel_btn = types.InlineKeyboardButton("❌ Отмена", callback_data="cancel_game")
    markup.add(publish_btn, cancel_btn)

    bot.send_message(chat_id, "Выберите действие:", reply_markup=markup)
