import telebot
import urllib.parse
import requests
import re
import random
from telebot import types
from collections import defaultdict, deque

TOKEN = '7691192017:AAFH2azoOy38TkucN3xiucy7sbVpxo8elcA'
bot = telebot.TeleBot(TOKEN)

search_count = 0
users = set()  # унікальні користувачі
user_history = defaultdict(lambda: deque(maxlen=3))  # історія до 3 пісень

random_songs = [
    "Shape of You Ed Sheeran",
    "Blinding Lights The Weeknd",
    "Someone Like You Adele",
    "Dance Monkey Tones and I",
    "Believer Imagine Dragons",
    "Montero Lil Nas X",
    "Closer The Chainsmokers",
    "Bad Guy Billie Eilish",
    "Sunflower Post Malone",
    "Señorita Shawn Mendes",
    "Perfect Ed Sheeran",
    "Havana Camila Cabello",
    "Girls Like You Maroon 5"
]

def get_video_info(search_query):
    search_url = f"https://www.youtube.com/results?search_query={urllib.parse.quote_plus(search_query)}"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(search_url, headers=headers)
    html = response.text

    video_ids = re.findall(r"watch\?v=(\S{11})", html)
    if not video_ids:
        return None

    video_id = video_ids[0]
    video_link = f"https://www.youtube.com/watch?v={video_id}"
    thumbnail_url = f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"

    title_match = re.search(r'"title":{"runs":\[{"text":"([^"]+)"\}', html)
    title = title_match.group(1) if title_match else "Назва не знайдена"

    return title, video_link, thumbnail_url

def get_main_menu():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("🎲 Випадкова пісня")
    keyboard.add("📊 Статистика", "🕘 Історія")
    return keyboard

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(
        message.chat.id,
        "Привіт! Напиши частину тексту пісні або скористайся меню нижче 🎶",
        reply_markup=get_main_menu()
    )

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    global search_count
    user_id = message.from_user.id
    users.add(user_id)  # Додаємо унікального користувача

    text = message.text.strip()

    if text == "📊 Статистика":
        bot.send_message(message.chat.id,
            f"📈 Всього пошуків: {search_count}\n👥 Користувачів бота: {len(users)}"
        )
        return

    if text == "🕘 Історія":
        history = list(user_history[user_id])
        if history:
            response = "\n".join([f"{i+1}. {song}" for i, song in enumerate(reversed(history))])
            bot.send_message(message.chat.id, f"🕘 Останні пісні:\n{response}")
        else:
            bot.send_message(message.chat.id, "У тебе ще немає історії 😕")
        return

    if text == "🎲 Випадкова пісня":
        query = random.choice(random_songs) + " lyrics"
    else:
        query = text + " lyrics"

    info = get_video_info(query)

    if info:
        title, link, thumbnail = info
        user_history[user_id].append(title)
        search_count += 1
        caption = f"🔍 {title}\n🎧 {link}"  # Без markdown
        bot.send_photo(message.chat.id, photo=thumbnail, caption=caption)
    else:
        bot.send_message(message.chat.id, "Нічого не знайдено. Спробуй іншу фразу 🔍")

bot.polling(none_stop=True)
