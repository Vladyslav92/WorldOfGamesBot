from collections import defaultdict
from datetime import datetime
import json


def write_json_file(data, filename):
    try:
        with open(filename, 'r+', encoding='utf-8') as file:
            try:
                file_data = json.load(file)
                file_data.append(data)
                file.seek(0)
                json.dump(file_data, file, ensure_ascii=False, indent=4)
            except json.JSONDecodeError:
                file.seek(0)
                json.dump([data], file, ensure_ascii=False, indent=4)
    except FileNotFoundError:
        with open(filename, 'w', encoding='utf-8') as file:
            json.dump([data], file, ensure_ascii=False, indent=4)


def calculate_player_success(matches, player_name):
    total_points = 0
    total_matches = 0

    for match in matches:
        for key in match:
            if key.startswith("player") and isinstance(match[key], list) and match[key][0] == player_name:
                total_points += match[key][1]
                total_matches += 1
                break

    if total_matches == 0:
        return "Игрок не найден"

    success_rate = (total_points / total_matches) / 100
    return f"[{success_rate:.0%}]"


def gather_statistics(data):
    stats = defaultdict(int)  # Считаем общее количество матчей для каждого игрока
    for entry in data:
        for key, value in entry.items():
            if key.startswith('player'):
                player_str = value[0]  # Учитываем только имя игрока, без очков
                stats[player_str] += 1
    return stats


def player_check(player, entry, stats, matches):
    numbers_dict = {
        'player1': '🥇', 'player2': '🥈', 'player3': '🥉', 'player4': '4️⃣', 'player5': '5️⃣',
        'player6': '6️⃣', 'player7': '7️⃣', 'player8': '8️⃣', 'player9': '9️⃣', 'player10': '🔟'
    }
    emoji_titles = ['👑', '📚', '◼️', '🪖']
    for key, value in entry.items():
        if value == player and key.startswith('player'):
            player_str = value[0]  # Учитываем только имя игрока, без очков
            games_played = stats[player_str]
            if games_played >= 10:
                success_rate = calculate_player_success(matches, value[0])  # Добавляем успех игрока
            else:
                success_rate = ''  # Не добавляем успех для игроков с менее чем 10 матчами
            if games_played == 1 or games_played == 2:
                title_emoji = emoji_titles[1]
            elif 2 < games_played <= 9:
                title_emoji = emoji_titles[2]
            elif games_played == 10:
                title_emoji = emoji_titles[3]
            elif games_played > 10:
                title_emoji = emoji_titles[0]
            else:
                title_emoji = ''
            emoji = numbers_dict.get(key, '')
            return f'{emoji} {title_emoji} {value[0]} {success_rate}'
    return player


def read_json_file(filename=None):
    if filename is None:
        return "Нет данных в базе"
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            try:
                data = json.load(file)
            except json.JSONDecodeError:
                return 'Нет информации в базе'
    except FileNotFoundError:
        return 'Файл не найден'

    stats = gather_statistics(data)
    result = []
    for entry in data:
        players = '\n'.join([
            f'{player_check(entry[f"player{i + 1}"], entry, stats, data)} '
            f'{entry[f"player{i + 1}"][1]} 🎳' for i in range(entry["number_players"])])

        result.append(f'\n`{entry["date"]}`\n'
                      f'\n        *\\<\\<{entry["game_name"].replace(".", "\\.").replace("-", "\\-").replace("_", "\\_")}\\>\\>*\n'
                      f'      👥 Участников: {entry["number_players"]}\n'
                      f'{players}\n'
                      f'      *🗞️ Правила*: *{entry["rules"]}*\n'
                      f'      *⏳ Партия*: *{entry["party"]}*\n'
                      f'      _🏆 Набрано_: {entry[f"player1"][-1]}\n')

    return ''.join(result)


def to_base(message=None):
    now = datetime.now().strftime('%d.%m.%Y | %H:%M')
    data = {
        "date": now,
        "game_name": message[0],
        "number_players": message[1]
    }
    for i, player in enumerate(message[2]):
        data[f'player{i + 1}'] = player

    data["rules"] = message[3]
    data["party"] = message[4]
    write_json_file(data, 'base/data.json')


if __name__ == '__main__':
    to_base()
    read_json_file()
