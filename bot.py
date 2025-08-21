import telebot
import re
from telebot import types
from base.base import to_base, read_json_file

TOKEN = ''
bot = telebot.TeleBot(TOKEN)
GAME_INFO = []
base = []


# Функция обработки команды start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    # Создаем основное меню с одной кнопкой
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    CreateGameButton = types.KeyboardButton("📂 Создать игру")
    GamesOnWeekButton = types.KeyboardButton("📂 Игры на неделе")
    ProfileButton = types.KeyboardButton("👤 Профиль")
    InfoButton = types.KeyboardButton("📃 Инфо")
    markup.add(CreateGameButton, GamesOnWeekButton)
    markup.add(ProfileButton, InfoButton)

    # Отправляем сообщение с кнопкой "Старт"
    bot.send_message(message.chat.id, "Главное меню:", reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == "📃 Инфо")
def info_button(message):
    bot.send_message(message.chat.id, "<Тут будет информация>")


@bot.message_handler(func=lambda message: message.text == "👤 Профиль")
def profile_button(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    MyParticipationButton = types.KeyboardButton("🎲 Мои участия")
    MyGamesButton = types.KeyboardButton("🎲 Мои игры")
    FriendsButton = types.KeyboardButton("👤 Друзья")
    ReturnButton = types.KeyboardButton("📂 Вернуться в меню")
    markup.add(MyParticipationButton, MyGamesButton)
    markup.add(FriendsButton, ReturnButton)

    bot.send_message(message.chat.id, "👤 Профиль:", reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == "📂 Игры на неделе")
def games_onweek_button(message):
    bot.send_message(message.chat.id, "📂 Пока нет доступных игр")


@bot.message_handler(func=lambda message: message.text == "📂 Создать игру")
def create_game_button(message):
    empty_markup = types.ReplyKeyboardRemove()
    bot.send_message(message.chat.id, "🎮 Введите название игры (например: 'NewGame'):", reply_markup=empty_markup)
    bot.register_next_step_handler(message, handle_game_name_from_create_game)


def handle_game_name_from_create_game(message):
    game_name = message.text.strip()
    if not game_name:
        bot.send_message(message.chat.id, "❌ Название игры не может быть пустым. Попробуйте снова:")
        bot.register_next_step_handler(message, handle_game_name_from_create_game)
        return

    # Инициализируем создание отчёта с уже введённым названием
    global GAME_INFO, base
    GAME_INFO = [game_name]
    base = []
    bot.send_message(message.chat.id, "👥 Введите количество игроков (например: '3'):")
    bot.register_next_step_handler(message, get_number_of_players)


@bot.message_handler(func=lambda message: message.text == "🎲 Мои участия")
def participation_button(message):
    empty_markup = types.ReplyKeyboardRemove()
    bot.send_message(message.chat.id, "🕖 Ожидайте", reply_markup=empty_markup)

    markup = types.ReplyKeyboardMarkup()
    CreateReportButton = types.KeyboardButton("📂 Создать отчет")
    ShowReportButton = types.KeyboardButton("📂 Посмотреть отчеты")
    ReturnButton = types.KeyboardButton("📂 Вернуться в меню")
    markup.add(CreateReportButton, ShowReportButton)
    markup.add(ReturnButton)

    bot.send_message(message.chat.id, "🎮 Ваши участия:", reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == "📂 Создать отчет")
def create_report(message):
    global GAME_INFO, base
    GAME_INFO = []
    base = []
    bot.send_message(message.chat.id, "🎮 Введите название игры (например: 'GameName'):")
    bot.register_next_step_handler(message, get_game_name)


def get_game_name(message):
    game_name = message.text.strip()
    if not game_name:
        bot.send_message(message.chat.id, "❌ Название игры не может быть пустым. Попробуйте снова:")
        bot.register_next_step_handler(message, get_game_name)
        return
    GAME_INFO.append(game_name)
    bot.send_message(message.chat.id, "👥 Введите количество игроков (например: '3'):")
    bot.register_next_step_handler(message, get_number_of_players)


def get_number_of_players(message):
    text = message.text.strip()
    match = re.search(r'\d+', text)
    if not match:
        bot.send_message(message.chat.id, "❌ Введите хотя бы одно число. Попробуйте снова:")
        bot.register_next_step_handler(message, get_number_of_players)
        return
    num_players = int(match.group())
    GAME_INFO.append(num_players)
    bot.send_message(message.chat.id,
                     f"👤 Введите данные игрока 1 в формате: '@ник Имя 10'\n(где 10 — очки):")
    bot.register_next_step_handler(message, get_player_info, 1, num_players)


def get_player_info(message, player, num_players):
    global base
    text = message.text.strip()
    parts = text.split()

    if len(parts) != 3 or not parts[0].startswith('@') or not parts[2].isdigit() or ' ' in parts[1]:
        bot.send_message(message.chat.id,
                         f"❌ Неверный формат. Введите данные игрока {player} в формате: '@ник Имя 10'")
        bot.register_next_step_handler(message, get_player_info, player, num_players)
        return

    username = parts[0]
    nickname = parts[1]
    score = int(parts[2])
    base.append((f"{username} {nickname}", score))

    if player >= num_players:
        GAME_INFO.append(base)
        bot.send_message(message.chat.id, "📜 Введите правила игры (например: '20м' или '2ч' или '2ч 15м'):")
        bot.register_next_step_handler(message, get_rules)
    else:
        bot.send_message(message.chat.id,
                         f"👤 Введите данные игрока {player + 1} в формате: '@ник Имя 10'")
        bot.register_next_step_handler(message, get_player_info, player + 1, num_players)


def get_rules(message):
    text = message.text.strip()

    # Проверка на допустимые форматы: "20м", "2ч", "1ч 30м"
    pattern = r'^((\d{1,2}ч)?\s?(\d{1,2}м)?)$'
    match = re.match(pattern, text)

    if not match:
        bot.send_message(message.chat.id,
                         "❌ Неверный формат. Примеры: '20м', '2ч', '1ч 30м'")
        bot.register_next_step_handler(message, get_rules)
        return

    # Проверка диапазонов
    hours_match = re.search(r'(\d{1,2})ч', text)
    minutes_match = re.search(r'(\d{1,2})м', text)

    if hours_match:
        hours = int(hours_match.group(1))
        if not (1 <= hours <= 24):
            bot.send_message(message.chat.id, "❌ Часы должны быть от 1 до 24. Попробуйте снова:")
            bot.register_next_step_handler(message, get_rules)
            return

    if minutes_match:
        minutes = int(minutes_match.group(1))
        if not (1 <= minutes <= 60):
            bot.send_message(message.chat.id, "❌ Минуты должны быть от 1 до 60. Попробуйте снова:")
            bot.register_next_step_handler(message, get_rules)
            return

    GAME_INFO.append(text)
    bot.send_message(message.chat.id,
                     "⏳ Введите длительность партии (например: '2ч 15м', '2ч', или '45м'):")
    bot.register_next_step_handler(message, get_to_base)


def get_to_base(message):
    text = message.text.strip()
    pattern = r'^((\d{1,2}ч)?\s?(\d{1,2}м)?)$'
    match = re.match(pattern, text)

    if not match:
        bot.send_message(message.chat.id,
                         "❌ Неверный формат. Примеры: '2ч 15м', '2ч', '45м'")
        bot.register_next_step_handler(message, get_to_base)
        return

    # Проверка диапазонов
    hours_match = re.search(r'(\d{1,2})ч', text)
    minutes_match = re.search(r'(\d{1,2})м', text)

    if hours_match:
        hours = int(hours_match.group(1))
        if not (1 <= hours <= 24):
            bot.send_message(message.chat.id, "❌ Часы должны быть от 1 до 24. Попробуйте снова:")
            bot.register_next_step_handler(message, get_to_base)
            return

    if minutes_match:
        minutes = int(minutes_match.group(1))
        if not (1 <= minutes <= 60):
            bot.send_message(message.chat.id, "❌ Минуты должны быть от 1 до 60. Попробуйте снова:")
            bot.register_next_step_handler(message, get_to_base)
            return

    GAME_INFO.append(text)
    to_base(GAME_INFO)
    bot.send_message(message.chat.id, "✅ Отчет сохранен в базе данных.")
    send_welcome(message)


@bot.message_handler(func=lambda message: message.text == "📂 Посмотреть отчеты")
def show_reports(message):
    report = read_json_file("base/data.json")

    # Telegram ограничивает длину сообщений до 4096 символов
    max_message_length = 4096

    # Разбиваем отчет на части
    for i in range(0, len(report), max_message_length):
        bot.send_message(message.chat.id, report[i:i + max_message_length], parse_mode='MarkdownV2')


@bot.message_handler(func=lambda message: message.text == "🎲 Мои игры")
def my_games_button(message):
    bot.send_message(message.chat.id, "Пока вы не создавали никаких постов")


# ЭТА ФУНКЦИЯ В БУДУЩЕМ БУДЕТ ПЕРЕПИСАНА И УСЛОЖНЕНА
@bot.message_handler(func=lambda message: message.text == "👤 Друзья")
def my_friends_button(message):
    # Создаем разметку с кнопкой "Искать друзей"
    inline_markup = types.InlineKeyboardMarkup()
    FindFriendsButton = types.InlineKeyboardButton("🔎 Искать друзей", callback_data='find_friends')
    inline_markup.add(FindFriendsButton)
    # Отправляем сообщение с кнопкой "Искать друзей"
    bot.send_message(message.chat.id, "👥 Вы пока не добавили друзей", reply_markup=inline_markup)


# ЭТА ФУНКЦИЯ В БУДУЩЕМ БУДЕТ ПЕРЕПИСАНА И УСЛОЖНЕНА
@bot.callback_query_handler(func=lambda call: call.data == 'find_friends')
def find_friends_operation(call):
    empty_markup = types.ReplyKeyboardRemove()
    bot.send_message(call.message.chat.id, "🕖 Подождите", reply_markup=empty_markup)
    markup = types.InlineKeyboardMarkup()
    CancelButton = types.InlineKeyboardButton("⏪ Вернуться", callback_data='cancel')
    markup.add(CancelButton)
    bot.send_message(call.message.chat.id, "🔎 Введите имя пользователя для поиска:", reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == "📂 Вернуться в меню")
def return_to_menu(message):
    send_welcome(message)


# Обработка нажатия кнопки "Отменить"
@bot.callback_query_handler(func=lambda call: call.data == 'cancel')
def cancel_operation(call):
    send_welcome(call.message)


# Запуск бота
bot.polling(none_stop=True, interval=0)
