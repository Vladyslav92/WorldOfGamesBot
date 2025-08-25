import json
from datetime import datetime
from telebot import TeleBot

GAMES_FILE = "base/games.json"
MAX_MESSAGE_LENGTH = 4096


def show_upcoming_games(bot: TeleBot, message):
    try:
        with open(GAMES_FILE, "r", encoding="utf-8") as f:
            games = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        bot.send_message(message.chat.id, "⚠️ Не удалось загрузить список игр.")
        return

    today = datetime.today().date()
    valid_games = {}

    # Фильтруем и удаляем устаревшие игры
    for name, game in games.items():
        try:
            game_date = datetime.strptime(game["date"], "%d.%m.%Y").date()
            if game_date >= today:
                valid_games[name] = game
        except ValueError:
            continue  # Пропускаем некорректные даты

    # Обновляем файл без устаревших игр
    with open(GAMES_FILE, "w", encoding="utf-8") as f:
        json.dump(valid_games, f, ensure_ascii=False, indent=4)

    if not valid_games:
        bot.send_message(message.chat.id, "📭 Нет предстоящих игр.")
        return

    # Сортируем игры по дате
    sorted_games = sorted(
        valid_games.values(),
        key=lambda g: datetime.strptime(g["date"], "%d.%m.%Y")
    )

    # Формируем текст отчётов
    messages = []
    current_message = ""

    for game in sorted_games:
        summary = (
            f"🎲 *{game['game_name']}*\n"
            f"🗓 {game['date']} ({game['weekday']})\n"
            f"🕓 {game['time']}\n"
            f"👥 Игроков: {game['players']}, Резерв: {game['reserve']}\n"
            f"📚 Обучение: {game['training']}, Партия: {game['party']}\n"
            f"💬 {game['comment']}\n\n"
        )

        if len(current_message) + len(summary) > MAX_MESSAGE_LENGTH:
            messages.append(current_message)
            current_message = summary
        else:
            current_message += summary

    if current_message:
        messages.append(current_message)

    # Отправляем сообщения
    for msg in messages:
        bot.send_message(message.chat.id, msg, parse_mode="Markdown")
