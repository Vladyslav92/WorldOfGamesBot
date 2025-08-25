MAX_MESSAGE_LENGTH = 4096
INFO_FILE = "modules/info.txt"


def show_info(bot, message):
    try:
        with open(INFO_FILE, "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        bot.send_message(message.chat.id, "⚠️ Файл с информацией не найден.")
        return

    # Разбиваем длинный текст
    chunks = [content[i:i + MAX_MESSAGE_LENGTH] for i in range(0, len(content), MAX_MESSAGE_LENGTH)]

    for chunk in chunks:
        bot.send_message(message.chat.id, chunk)
