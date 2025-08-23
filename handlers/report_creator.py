from WorldOfGamesBot.base.base import to_base
import re

GAME_INFO = []
base = []


def create_report(bot, message):
    global GAME_INFO, base
    GAME_INFO = []
    base = []
    bot.send_message(message.chat.id, "🎮 Введите название игры (например: 'GameName'):")
    bot.register_next_step_handler(message, lambda msg: get_game_name(bot, msg))


def get_game_name(bot, message):
    game_name = message.text.strip()
    if not game_name:
        bot.send_message(message.chat.id, "❌ Название игры не может быть пустым. Попробуйте снова:")
        bot.register_next_step_handler(message, lambda msg: get_game_name(bot, msg))
        return
    GAME_INFO.append(game_name)
    bot.send_message(message.chat.id, "👥 Введите количество игроков (например: '3'):")
    bot.register_next_step_handler(message, lambda msg: get_number_of_players(bot, msg))


def get_number_of_players(bot, message):
    text = message.text.strip()
    match = re.search(r'\d+', text)
    if not match:
        bot.send_message(message.chat.id, "❌ Введите хотя бы одно число. Попробуйте снова:")
        bot.register_next_step_handler(message, lambda msg: get_number_of_players(bot, msg))
        return
    num_players = int(match.group())
    GAME_INFO.append(num_players)
    bot.send_message(message.chat.id,
                     f"👤 Введите данные игрока 1 в формате: '@ник Имя 10'")
    bot.register_next_step_handler(message, lambda msg: get_player_info(bot, msg, 1, num_players))


def get_player_info(bot, message, player, num_players):
    global base
    text = message.text.strip()
    parts = text.split()

    if len(parts) != 3 or not parts[0].startswith('@') or not parts[2].isdigit() or ' ' in parts[1]:
        bot.send_message(message.chat.id,
                         f"❌ Неверный формат. Введите данные игрока {player} в формате: '@ник Имя 10'")
        bot.register_next_step_handler(message, lambda msg: get_player_info(bot, msg, player, num_players))
        return

    username = parts[0]
    nickname = parts[1]
    score = int(parts[2])
    base.append((f"{username} {nickname}", score))

    if player >= num_players:
        GAME_INFO.append(base)
        bot.send_message(message.chat.id, "📜 Введите правила игры (например: '20м'):")
        bot.register_next_step_handler(message, lambda msg: get_rules(bot, msg))
    else:
        bot.send_message(message.chat.id,
                         f"👤 Введите данные игрока {player + 1} в формате: '@ник Имя 10'")
        bot.register_next_step_handler(message, lambda msg: get_player_info(bot, msg, player + 1, num_players))


def get_rules(bot, message):
    text = message.text.strip()
    pattern = r'^((\d{1,2}ч)?\s?(\d{1,2}м)?)$'
    match = re.match(pattern, text)

    if not match:
        bot.send_message(message.chat.id,
                         "❌ Неверный формат. Примеры: '20м', '2ч', '1ч 30м'")
        bot.register_next_step_handler(message, lambda msg: get_rules(bot, msg))
        return

    hours_match = re.search(r'(\d{1,2})ч', text)
    minutes_match = re.search(r'(\d{1,2})м', text)

    if hours_match and not (1 <= int(hours_match.group(1)) <= 24):
        bot.send_message(message.chat.id, "❌ Часы должны быть от 1 до 24. Попробуйте снова:")
        bot.register_next_step_handler(message, lambda msg: get_rules(bot, msg))
        return

    if minutes_match and not (1 <= int(minutes_match.group(1)) <= 60):
        bot.send_message(message.chat.id, "❌ Минуты должны быть от 1 до 60. Попробуйте снова:")
        bot.register_next_step_handler(message, lambda msg: get_rules(bot, msg))
        return

    GAME_INFO.append(text)
    bot.send_message(message.chat.id, "⏳ Введите длительность партии (например: '2ч 15м', '2ч', или '45м'):")
    bot.register_next_step_handler(message, lambda msg: get_to_base(bot, msg))


def get_to_base(bot, message):
    text = message.text.strip()
    pattern = r'^((\d{1,2}ч)?\s?(\d{1,2}м)?)$'
    match = re.match(pattern, text)

    if not match:
        bot.send_message(message.chat.id,
                         "❌ Неверный формат. Примеры: '2ч 15м', '2ч', '45м'")
        bot.register_next_step_handler(message, lambda msg: get_to_base(bot, msg))
        return

    hours_match = re.search(r'(\d{1,2})ч', text)
    minutes_match = re.search(r'(\d{1,2})м', text)

    if hours_match and not (1 <= int(hours_match.group(1)) <= 24):
        bot.send_message(message.chat.id, "❌ Часы должны быть от 1 до 24. Попробуйте снова:")
        bot.register_next_step_handler(message, lambda msg: get_to_base(bot, msg))
        return

    if minutes_match and not (1 <= int(minutes_match.group(1)) <= 60):
        bot.send_message(message.chat.id, "❌ Минуты должны быть от 1 до 60. Попробуйте снова:")
        bot.register_next_step_handler(message, lambda msg: get_to_base(bot, msg))
        return

    GAME_INFO.append(text)
    to_base(GAME_INFO)
    bot.send_message(message.chat.id, "✅ Отчет сохранен в базе данных.")
