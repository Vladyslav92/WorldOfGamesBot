import telebot
from telebot import types
from base.base import read_json_file
from handlers.report_creator import create_report


with open("TOKEN.txt", "r") as f:
    TOKEN = f.read().strip()

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
    bot.send_message(message.chat.id, "🕖 Ожидайте", reply_markup=empty_markup)

    markup = types.InlineKeyboardMarkup()
    CancelButton = types.InlineKeyboardButton("❌ Отменить", callback_data='cancel')
    markup.add(CancelButton)

    bot.send_message(message.chat.id, "🎮 Введите название игры:", reply_markup=markup)


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
def create_report_handler(message):
    create_report(bot, message)


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
