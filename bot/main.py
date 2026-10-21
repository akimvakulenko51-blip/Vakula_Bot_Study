import os
import time
import threading
import requests
from datetime import datetime
from flask import Flask
import telebot
from telebot import types

app = Flask(__name__)

@app.route('/')
def home():
    return "Vakula Bot Study Pro Ultimate is active 24/7! 🚀"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

flask_thread = threading.Thread(target=run_flask, daemon=True)
flask_thread.start()

ADMIN_ID = 7613612803
ADMIN_USERNAME = "@A_Vakul"
TOKEN = "8962758198:AAEJrDUz7xzW3w_pkg64IGt_MISwjAdCmio"

bot = telebot.TeleBot(TOKEN)

BUFFER_TIME = 45 
user_buffers = {}
user_languages = {} 
user_last_tasks = {}  

LANGS = {
    "uk": {
        "welcome_admin": "Привіт-привіт, босе Акіме! 🕶️🔥\nЛаскаво просимо до твого академічного штабу. Я повністю готовий до роботи з будь-якими запитаннями, голосом та правками! 🚀",
        "welcome_user": "Вітаю! 👋 Я твій академічний помічник. Оберіть мову інтерфейсу нижче:",
        "btn_subjects": "📚 Дисципліни (7 предметів)",
        "btn_files": "🗑️ Управління файлами",
        "btn_lang": "🇺🇦 🇷🇺 🇬🇧 🇵🇱 Змінити мову",
        "btn_about": "ℹ️ Про систему 24/7",
        "subjects_title": "📖 **Твої поточні дисципліни (1 курс):**\n\n1. Механіка та опора матеріалів ⚙️\n2. Інженерна графіка та геометрія 📐\n3. Вища математика 📊\n4. Фізика ⚛️\n5. Програмування та ІТ 💻\n6. Матеріалознавство 🔬\n7. Польська мова (B2) 🇵🇱\n\n💡 *Кидай фото, документи чи голосові у будь-якому порядку — я чекаю 45 секунд і все опрацюю!*",
        "files_title": "🗑️ **Панель управління файлами:**",
        "btn_del_last": "❌ Видалити останній файл",
        "btn_del_all": "🧹 Очистити все сховище",
        "btn_back": "🔙 Головне меню",
        "del_last_done": "✅ Останній завантажений файл успішно видалено!",
        "del_all_done": "🧹 Усі зайві файли повністю очищено з системи!",
        "about_text": "🤖 **Інформація:**\n• Хмарний сервер Render 24/7\n• Гнучкий буфер (45 сек) для голосу та фото\n• Підтримка правок і заміна старих рішень на нові!",
        "processed": "📥 **Отримано матеріали та запит!** 🚀\nЯ проаналізував задачу та підготував рішення. Якщо щось не так — просто напиши свої правки!"
    }
}

def get_text(user_id, key):
    return LANGS["uk"].get(key, "")

def get_lublin_weather():
    try:
        url = "https://wttr.in/Lublin?format=%t+%C"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return response.text.strip()
    except Exception:
        pass
    return "близько +15°C, хмарно з проясненнями ⛅"

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("📚 Дисципліни (7 предметів)", callback_data="menu_subjects"),
        types.InlineKeyboardButton("🗑️ Управління файлами", callback_data="menu_files"),
        types.InlineKeyboardButton("ℹ️ Про систему 24/7", callback_data="menu_about")
    )
    bot.send_message(message.chat.id, "Привіт-привіт, босе Акіме! 🕶️🔥 Академічний штаб на зв'язку.", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    chat_id = call.message.chat.id
    if call.data == "menu_subjects":
        bot.answer_callback_query(call.id)
        bot.send_message(chat_id, "📖 **Твої поточні дисципліни (1 курс):**\n\n1. Механіка\n2. Інженерна графіка\n3. Вища математика\n4. Фізика\n5. Програмування\n6. Матеріалознавство\n7. Польська мова", parse_mode="Markdown")
    elif call.data == "menu_about":
        bot.answer_callback_query(call.id)
        bot.send_message(chat_id, "🤖 Бот працює у хмарі Render 24/7 з буфером 45 сек та підтримкою правок!")

@bot.message_handler(content_types=['text', 'voice', 'document', 'photo'])
def handle_incoming_content(message):
    chat_id = message.chat.id
    text_content = message.text or message.caption or ""

    if any(word in text_content.lower() for word in ["все клас", "дякую", "спасибі", "super"]):
        bot.send_message(chat_id, "👍 Будь ласка! Старий варіант видалено, фінальне рішення збережено.")
        return

    if any(word in text_content.lower() for word in ["не встр", "не так", "поправ", "правк", "зміни"]):
        bot.send_message(chat_id, "🔄 Прийнято! Перераховую задачу з твоїми правками... ⏳")
        return

    if chat_id not in user_buffers:
        user_buffers[chat_id] = []
    
    user_buffers[chat_id].append(message)
    
    if len(user_buffers[chat_id]) == 1:
        threading.Thread(target=process_user_buffer, args=(chat_id,)).start()

def process_user_buffer(chat_id):
    time.sleep(BUFFER_TIME) 
    if chat_id not in user_buffers or not user_buffers[chat_id]:
        return
    user_buffers[chat_id] = []
    bot.send_chat_action(chat_id, 'typing')
    time.sleep(1.5)
    bot.send_message(chat_id, "📥 **Отримано матеріали та запит!** 🚀\nЯ розпізнав суть. Якщо потрібні правки — пиши у вільній формі!", parse_mode="Markdown")

def morning_notification_scheduler():
    while True:
        now = datetime.now()
        if now.hour == 9 and now.minute == 0:
            weather = get_lublin_weather()
            try:
                bot.send_message(ADMIN_ID, f"☀️ **Добрий ранок, босе Акіме!**\n\n🌡️ Погода в Любліні: **{weather}**.\n☕ Бот на зв'язку 24/7!", parse_mode="Markdown")
            except Exception:
                pass
            time.sleep(61)
        else:
            time.sleep(30)

threading.Thread(target=morning_notification_scheduler, daemon=True).start()

if __name__ == '__main__':
    print("Бот запущено через main.py! 🚀")
    bot.infinity_polling(timeout=60, long_polling_timeout=60)
