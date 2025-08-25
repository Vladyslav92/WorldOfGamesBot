import telebot
from telebot import types
from base.base import read_json_file
from handlers.report_creator import create_report
from handlers.game_creator import create_game, register_game_handlers
from handlers.game_editor import request_game_edit, register_edit_handlers, request_game_deletion
from handlers.find_games import show_upcoming_games
from modules.info_display import show_info

with open("TOKEN.txt", "r") as f:
    TOKEN = f.read().strip()

bot = telebot.TeleBot(TOKEN)
GAME_INFO = []
base = []


@bot.message_handler(commands=['start'])
def start_command(message):
    send_welcome(bot, message)


def send_welcome(bot, message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    CreateGameButton = types.KeyboardButton("📂 Создать игру")
    FutureGamesButton = types.KeyboardButton("📂 Предстоящие игры")
    ProfileButton = types.KeyboardButton("👤 Профиль")
    InfoButton = types.KeyboardButton("📃 Инфо")
    markup.add(CreateGameButton, FutureGamesButton)
    markup.add(ProfileButton, InfoButton)

    bot.send_message(message.chat.id, "Главное меню:", reply_markup=markup)


register_game_handlers(bot, send_welcome)
register_edit_handlers(bot, send_welcome)


@bot.message_handler(func=lambda message: message.text == "📃 Инфо")
def info_button(message):
    show_info(bot, message)


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


@bot.message_handler(func=lambda message: message.text == "📂 Предстоящие игры")
def future_games_button(message):
    show_upcoming_games(bot, message)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    EditButton = types.KeyboardButton("✏️ Изменить предстоящую игру")
    DeleteButton = types.KeyboardButton("🗑 Удалить игру")
    ReturnButton = types.KeyboardButton("📂 Вернуться в меню")
    markup.add(EditButton, DeleteButton)
    markup.add(ReturnButton)

    bot.send_message(message.chat.id, "Выберите действие:", reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == "🗑 Удалить игру")
def delete_game_button(message):
    request_game_deletion(bot, message, send_welcome)


@bot.message_handler(func=lambda message: message.text == "✏️ Изменить предстоящую игру")
def edit_game_button(message):
    request_game_edit(bot, message, send_welcome)


@bot.message_handler(func=lambda message: message.text == "📂 Создать игру")
def create_game_button(message):
    create_game(bot, message)


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
    max_message_length = 4096
    for i in range(0, len(report), max_message_length):
        bot.send_message(message.chat.id, report[i:i + max_message_length], parse_mode='MarkdownV2')


@bot.message_handler(func=lambda message: message.text == "🎲 Мои игры")
def my_games_button(message):
    bot.send_message(message.chat.id, "Пока вы не создавали никаких постов")


@bot.message_handler(func=lambda message: message.text == "👤 Друзья")
def my_friends_button(message):
    inline_markup = types.InlineKeyboardMarkup()
    FindFriendsButton = types.InlineKeyboardButton("🔎 Искать друзей", callback_data='find_friends')
    inline_markup.add(FindFriendsButton)
    bot.send_message(message.chat.id, "👥 Вы пока не добавили друзей", reply_markup=inline_markup)
    send_welcome(bot, message)


@bot.callback_query_handler(func=lambda call: call.data == 'find_friends')
def find_friends_operation(call):
    empty_markup = types.ReplyKeyboardRemove()
    bot.send_message(call.message.chat.id, "🕖 Подождите", reply_markup=empty_markup)
    markup = types.InlineKeyboardMarkup()
    CancelButton = types.InlineKeyboardButton("⏪ Вернуться", callback_data='cancel')
    markup.add(CancelButton)
    bot.send_message(call.message.chat.id, "🔎 Введите имя пользователя для поиска:", reply_markup=markup)
    send_welcome(bot, call.message)


@bot.message_handler(func=lambda message: message.text == "📂 Вернуться в меню")
def return_to_menu(message):
    send_welcome(bot, message)


@bot.callback_query_handler(func=lambda call: call.data == 'cancel')
def cancel_operation(call):
    send_welcome(bot, call.message)


bot.polling(none_stop=True, interval=0)
