import json
import re
from datetime import datetime
from telebot import types
from telebot import TeleBot

GAMES_PATH = "base/games.json"
edit_sessions = {}


def request_game_deletion(bot: TeleBot, message, send_welcome):
    bot.send_message(message.chat.id, "🗑 Введите название игры, которую желаете удалить:")
    bot.register_next_step_handler(message, lambda msg: handle_game_deletion(bot, msg, send_welcome))


def handle_game_deletion(bot: TeleBot, message, send_welcome):
    game_name = message.text.strip()
    chat_id = message.chat.id

    try:
        with open(GAMES_PATH, "r", encoding="utf-8") as f:
            games = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        games = {}

    if game_name in games:
        del games[game_name]
        with open(GAMES_PATH, "w", encoding="utf-8") as f:
            json.dump(games, f, ensure_ascii=False, indent=4)

        bot.send_message(chat_id, f"✅ Игра *{game_name}* удалена из списка.", parse_mode="Markdown")
    else:
        bot.send_message(chat_id, (
            f"❌ Игры с названием *{game_name}* нет в базе данных.\n"
            "Проверьте ещё раз список будущих игр с названиями."
        ), parse_mode="Markdown")

    send_welcome(bot, message)


def request_game_edit(bot, message, send_welcome):
    bot.send_message(message.chat.id, "✏️ Введите название игры, детали которой желаете изменить:")
    bot.register_next_step_handler(message, lambda msg: start_edit_process(bot, msg, send_welcome))


def start_edit_process(bot, message, send_welcome):
    chat_id = message.chat.id
    original_name = message.text.strip()
    edit_sessions[chat_id] = {"original_name": original_name}
    bot.send_message(chat_id, "🔎 Введите новое название игры:")
    bot.register_next_step_handler(message, lambda msg: get_game_name_edit(bot, msg))


def get_game_name_edit(bot, message):
    chat_id = message.chat.id
    edit_sessions[chat_id]["game_name"] = message.text.strip()
    bot.send_message(chat_id, "🎲 Введите длительность обучения (например 30м, 1ч, 1ч 30м):")
    bot.register_next_step_handler(message, lambda msg: get_duration_edit(bot, msg, "training"))


def get_duration_edit(bot, message, key):
    chat_id = message.chat.id
    text = message.text.strip()
    pattern = r'^((\d{1,2}ч)?\s?(\d{1,2}м)?)$'
    match = re.match(pattern, text)

    if not match:
        bot.send_message(chat_id, "❌ Неверный формат. Примеры: '30м', '1ч', '1ч 30м'")
        bot.register_next_step_handler(message, lambda msg: get_duration_edit(bot, msg, key))
        return

    if "ч" in text:
        hours = int(re.search(r'(\d{1,2})ч', text).group(1))
        if not (1 <= hours <= 24):
            bot.send_message(chat_id, "❌ Часы должны быть от 1 до 24.")
            bot.register_next_step_handler(message, lambda msg: get_duration_edit(bot, msg, key))
            return

    if "м" in text:
        minutes = int(re.search(r'(\d{1,2})м', text).group(1))
        if not (1 <= minutes <= 60):
            bot.send_message(chat_id, "❌ Минуты должны быть от 1 до 60.")
            bot.register_next_step_handler(message, lambda msg: get_duration_edit(bot, msg, key))
            return

    edit_sessions[chat_id][key] = text
    if key == "training":
        bot.send_message(chat_id, "🎲 Введите длительность партии (например 30м, 1ч, 1ч 30м):")
        bot.register_next_step_handler(message, lambda msg: get_duration_edit(bot, msg, "party"))
    else:
        bot.send_message(chat_id, "📅 Введите дату начала (дд.мм.гггг):")
        bot.register_next_step_handler(message, lambda msg: get_date_edit(bot, msg))


def get_date_edit(bot, message):
    chat_id = message.chat.id
    text = message.text.strip()
    try:
        date_obj = datetime.strptime(text, "%d.%m.%Y")
        edit_sessions[chat_id]["date"] = date_obj
        bot.send_message(chat_id, "🕓 Введите время начала (например 14:00):")
        bot.register_next_step_handler(message, lambda msg: get_time_edit(bot, msg))
    except ValueError:
        bot.send_message(chat_id, "❌ Неверный формат. Введите дату в формате дд.мм.гггг")
        bot.register_next_step_handler(message, lambda msg: get_date_edit(bot, msg))


def get_time_edit(bot, message):
    chat_id = message.chat.id
    text = message.text.strip()
    try:
        time_obj = datetime.strptime(text, "%H:%M").time()
        edit_sessions[chat_id]["time"] = time_obj
        bot.send_message(chat_id, "👥 Введите количество игроков:")
        bot.register_next_step_handler(message, lambda msg: get_number_edit(bot, msg, "players"))
    except ValueError:
        bot.send_message(chat_id, "❌ Неверный формат. Введите время в формате ЧЧ:ММ")
        bot.register_next_step_handler(message, lambda msg: get_time_edit(bot, msg))


def get_number_edit(bot, message, key):
    chat_id = message.chat.id
    text = message.text.strip()

    if not text.isdigit():
        bot.send_message(chat_id, "❌ Введите число.")
        bot.register_next_step_handler(message, lambda msg: get_number_edit(bot, msg, key))
        return

    edit_sessions[chat_id][key] = int(text)

    if key == "players":
        bot.send_message(chat_id, "👥 Введите количество резервных мест:")
        bot.register_next_step_handler(message, lambda msg: get_number_edit(bot, msg, "reserve"))
    else:
        markup = types.InlineKeyboardMarkup()
        skip_button = types.InlineKeyboardButton("💳 Пропустить", callback_data="skip_comment_edit")
        markup.add(skip_button)
        bot.send_message(chat_id, "💬 Введите комментарий или нажмите кнопку ниже:", reply_markup=markup)
        bot.register_next_step_handler_by_chat_id(chat_id, lambda msg: handle_comment_edit(bot, msg))


def handle_comment_edit(bot, message):
    chat_id = message.chat.id

    if chat_id not in edit_sessions:
        bot.send_message(chat_id, "⚠️ Сессия редактирования не найдена. Попробуйте начать заново.")
        return

    edit_sessions[chat_id]["comment"] = message.text.strip()
    show_summary_edit(bot, chat_id)


def show_summary_edit(bot, chat_id):
    data = edit_sessions.get(chat_id, {})
    weekday_ru = {
        "Monday": "Понедельник", "Tuesday": "Вторник", "Wednesday": "Среда",
        "Thursday": "Четверг", "Friday": "Пятница", "Saturday": "Суббота", "Sunday": "Воскресенье"
    }

    date_obj = data["date"]
    weekday = date_obj.strftime("%A")
    date_str = date_obj.strftime("%d.%m.%Y")

    summary = (
        f"*🎲 {data['game_name']}*\n"
        f"🗓 {date_str} ({weekday_ru.get(weekday, weekday)})\n"
        f"🕓 {data['time'].strftime('%H:%M')}\n"
        f"👥 Игроков: {data['players']}, Резерв: {data['reserve']}\n"
        f"📚 Обучение: {data['training']}, Партия: {data['party']}\n"
        f"💬 {data.get('comment', '')}"
    )

    markup = types.InlineKeyboardMarkup()
    confirm_btn = types.InlineKeyboardButton("✅ Изменить", callback_data="confirm_edit")
    cancel_btn = types.InlineKeyboardButton("❌ Отменить", callback_data="cancel_edit")
    markup.add(confirm_btn, cancel_btn)

    bot.send_message(chat_id, summary, reply_markup=markup, parse_mode="Markdown")


def register_edit_handlers(bot, send_welcome):
    @bot.callback_query_handler(func=lambda call: call.data == "confirm_edit")
    def handle_confirm_edit(call):
        chat_id = call.message.chat.id
        data = edit_sessions.get(chat_id)

        if not data or "original_name" not in data or "game_name" not in data:
            bot.send_message(chat_id, "❌ Ошибка: данные для редактирования не найдены.")
            bot.answer_callback_query(call.id)
            return

        weekday = data["date"].strftime("%A")
        weekday_ru = {
            "Monday": "Понедельник", "Tuesday": "Вторник", "Wednesday": "Среда",
            "Thursday": "Четверг", "Friday": "Пятница", "Saturday": "Суббота", "Sunday": "Воскресенье"
        }

        game_entry = {
            "game_name": data["game_name"],
            "date": data["date"].strftime("%d.%m.%Y"),
            "weekday": weekday_ru.get(weekday, weekday),
            "time": data["time"].strftime("%H:%M"),
            "training": data["training"],
            "party": data["party"],
            "players": int(data["players"]),
            "reserve": int(data["reserve"]),
            "comment": data.get("comment", "")
        }

        try:
            with open(GAMES_PATH, "r", encoding="utf-8") as f:
                games = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            games = {}

        # Удаляем старую запись, если она существует
        if data["original_name"] in games:
            del games[data["original_name"]]

        # Сохраняем новую запись под новым названием
        games[data["game_name"]] = game_entry

        with open(GAMES_PATH, "w", encoding="utf-8") as f:
            json.dump(games, f, ensure_ascii=False, indent=4)

        edit_sessions.pop(chat_id, None)
        bot.answer_callback_query(call.id, f"✅ Игра *{data['game_name']}* успешно изменена!", show_alert=False)
        send_welcome(bot, call.message)

    @bot.callback_query_handler(func=lambda call: call.data == "cancel_edit")
    def handle_cancel_edit(call):
        chat_id = call.message.chat.id
        edit_sessions.pop(chat_id, None)
        bot.answer_callback_query(call.id, "❌ Изменение отменено.")
        send_welcome(bot, call.message)

    @bot.callback_query_handler(func=lambda call: call.data == "skip_comment_edit")
    def handle_skip_comment_edit(call):
        chat_id = call.message.chat.id

        if chat_id not in edit_sessions:
            bot.send_message(chat_id, "⚠️ Сессия редактирования не найдена. Попробуйте начать заново.")
            return

        edit_sessions[chat_id]["comment"] = ""
        bot.answer_callback_query(call.id)
        show_summary_edit(bot, chat_id)
