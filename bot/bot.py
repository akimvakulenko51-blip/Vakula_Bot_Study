import os
import time
import threading
import requests
from datetime import datetime
from flask import Flask
import telebot
from telebot import types
import google.generativeai as genai

# ==========================================
# 1. КОНФІГУРАЦІЯ ТА API КЛЮЧІ
# ==========================================
ADMIN_ID = 7613612803
ADMIN_USERNAME = "A_Vakul"
TELEGRAM_TOKEN = "8962758198:AAFvO2j9gdmjspxKnQORTYAyIbjTDvgva3I"

# ВСТАВ СВОЙ КЛЮЧ GEMINI СЮДА (У ЛАПКАХ):
GEMINI_API_KEY = "AQ.Ab8RN6KUYBT8VAK2sEkG473OlNSOkakqwZxr22CrxVvayZ8J3A"

genai.configure(api_key=GEMINI_API_KEY)
ai_model = genai.GenerativeModel('gemini-1.5-flash')

bot = telebot.TeleBot(TELEGRAM_TOKEN)
app = Flask(__name__)

@app.route('/')
def home():
    return "Vakula Bot Ultimate AI Pro is active 24/7! 🚀"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

threading.Thread(target=run_flask, daemon=True).start()

BUFFER_TIME = 45
user_buffers = {}
user_languages = {} 
user_last_tasks = {}      # Для правок
user_drafts = {}          # Тимчасова відповідь ШІ
user_saved_materials = {} # Затверджені (збережені) відповіді

# ==========================================
# 2. МАСШТАБНИЙ СЛОВНИК
# ==========================================
LANGS = {
    "uk": {
        "welcome_user": "Вітаю! 👋 Я твій академічний помічник Люблінської політехніки (1 курс, Механіка і будова машин).\n\nТут ти можеш переглядати дисципліни, розгорнуті новини університету та користуватися матеріалами.",
        "btn_subjects": "📚 Дисципліни (7 предметів)",
        "btn_files": "🗑️ Управління матеріалами",
        "btn_news": "📰 Новини університету",
        "btn_lang": "🇺🇦 🇷🇺 🇬🇧 🇵🇱 Змінити мову",
        "btn_about": "ℹ️ Про систему 24/7",
        "subjects_title": "📖 **Список твоїх дисциплін (1 курс — Механіка і будова машин):**\n\n1. Механіка та опора матеріалів ⚙️\n2. Інженерна графіка та геометрія 📐\n3. Вища математика 📊\n4. Фізика ⚛️\n5. Програмування та ІТ 💻\n6. Матеріалознавство 🔬\n7. Польська мова (B2) 🇵🇱",
        "files_title": "🗑️ **Панель матеріалів та збережених рішень:**",
        "btn_view_saved": "📂 Переглянути збережені відповіді",
        "btn_del_last": "❌ Видалити останній запит",
        "btn_del_all": "🧹 Очистити все сховище",
        "btn_back": "🔙 Головне меню",
        "del_last_done": "✅ Останній запит успішно видалено!",
        "del_all_done": "🧹 Усі збережені матеріали повністю очищено!",
        "news_title": "📰 **Новини (Люблінська політехніка):**\n\n• **Академічний процес:** Заняття проходять за розкладом на Велькопольській.\n• **Сесія:** Наближаються колоквіуми з вищої математики. Повторіть методички!",
        "about_text": "🤖 **Інформація:** Хмарний сервер Render 24/7 з підтримкою Gemini AI.",
    }
}

def get_text(user_id, key):
    return LANGS.get(user_languages.get(user_id, "uk"), LANGS["uk"]).get(key, LANGS["uk"][key])

def is_admin(user):
    return int(user.id) == ADMIN_ID or (user.username and user.username.lower() == ADMIN_USERNAME.lower())

def get_time_greeting():
    hour = datetime.now().hour
    if 5 <= hour < 12: return "Добрий ранок"
    elif 12 <= hour < 18: return "Добрий день"
    elif 18 <= hour < 23: return "Добрий вечір"
    else: return "Доброї ночі"

def get_lublin_weather():
    try:
        url = "https://wttr.in/Lublin?format=%t+%C"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return response.text.strip()
    except Exception:
        pass
    return "близько +15°C, хмарно ⛅"

# ==========================================
# 3. МЕНЮ ТА ІНТЕРФЕЙС
# ==========================================
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user = message.from_user
    if user.id not in user_languages:
        user_languages[user.id] = "uk"
    show_main_menu(message.chat.id, user, is_start=True)

def show_main_menu(chat_id, user, is_start=False):
    user_id = user.id
    time_greet = get_time_greeting()
    
    if is_admin(user):
        greeting = (
            f"😎🔥 **{time_greet}, босе Акіме!**\n\n"
            f"Академічний штаб (Політехніка Любельська, 1 курс). "
            f"ШІ-система готова: чекаю твої завдання, голосівки чи фото. Повний доступ активовано! 🚀"
        )
    else:
        greeting = get_text(user_id, "welcome_user")

    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton(get_text(user_id, "btn_subjects"), callback_data="menu_subjects"),
        types.InlineKeyboardButton(get_text(user_id, "btn_files"), callback_data="menu_files"),
        types.InlineKeyboardButton(get_text(user_id, "btn_news"), callback_data="menu_news"),
        types.InlineKeyboardButton(get_text(user_id, "btn_lang"), callback_data="menu_language"),
        types.InlineKeyboardButton(get_text(user_id, "btn_about"), callback_data="menu_about")
    )
    
    if is_start:
        bot.send_message(chat_id, greeting, reply_markup=markup, parse_mode="Markdown")
    else:
        try: bot.edit_message_text(greeting, chat_id, chat_id, reply_markup=markup, parse_mode="Markdown")
        except Exception: bot.send_message(chat_id, greeting, reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data.startswith("lang_") or call.data == "menu_language")
def language_handler(call):
    chat_id = call.message.chat.id
    if call.data == "menu_language":
        bot.answer_callback_query(call.id)
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton("🇺🇦 Укр", callback_data="lang_uk"),
            types.InlineKeyboardButton("🇷🇺 Рус", callback_data="lang_ru"),
            types.InlineKeyboardButton("🇬🇧 Eng", callback_data="lang_en"),
            types.InlineKeyboardButton("🇵🇱 Pol", callback_data="lang_pl")
        )
        markup.add(types.InlineKeyboardButton("🔙 Назад", callback_data="menu_back"))
        bot.edit_message_text("🌐 **Оберіть мову / Choose language:**", chat_id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")
        return
    user_languages[call.from_user.id] = call.data.split("_")[1]
    bot.answer_callback_query(call.id, "✨")
    show_main_menu(chat_id, call.from_user)

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    if call.data == "menu_subjects":
        bot.send_message(chat_id, get_text(user_id, "subjects_title"), parse_mode="Markdown")
    elif call.data == "menu_files":
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton(get_text(user_id, "btn_view_saved"), callback_data="view_saved"),
            types.InlineKeyboardButton(get_text(user_id, "btn_del_last"), callback_data="del_last"),
            types.InlineKeyboardButton(get_text(user_id, "btn_del_all"), callback_data="del_all"),
            types.InlineKeyboardButton(get_text(user_id, "btn_back"), callback_data="menu_back")
        )
        bot.send_message(chat_id, get_text(user_id, "files_title"), reply_markup=markup, parse_mode="Markdown")
    elif call.data == "view_saved":
        if user_id in user_saved_materials and user_saved_materials[user_id]:
            saved_text = user_saved_materials[user_id][-1]
            bot.send_message(chat_id, f"📂 **Твій останній збережений конспект:**\n\n{saved_text[:3900]}", parse_mode="Markdown")
        else:
            bot.send_message(chat_id, "📂 Твоє сховище поки що порожнє. Попроси ШІ щось вирішити і напиши «все клас», щоб зберегти сюди відповідь!")
    elif call.data == "del_last":
        if user_id in user_saved_materials and user_saved_materials[user_id]:
            user_saved_materials[user_id].pop()
        bot.send_message(chat_id, get_text(user_id, "del_last_done"))
    elif call.data == "del_all":
        user_saved_materials[user_id] = []
        bot.send_message(chat_id, get_text(user_id, "del_all_done"))
    elif call.data == "menu_news":
        bot.send_message(chat_id, get_text(user_id, "news_title"), parse_mode="Markdown")
    elif call.data == "menu_about":
        bot.send_message(chat_id, get_text(user_id, "about_text"), parse_mode="Markdown")
    elif call.data == "menu_back":
        show_main_menu(chat_id, call.from_user)
    bot.answer_callback_query(call.id)

# ==========================================
# 4. ШІ-БУФЕР ТА ПРАВКИ (ТІЛЬКИ АДМІН)
# ==========================================
@bot.message_handler(content_types=['text', 'voice', 'document', 'photo'])
def handle_incoming_content(message):
    chat_id = message.chat.id
    user = message.from_user

    if not is_admin(user):
        bot.send_message(chat_id, "👋 Студентський доступ: ШІ-розбір доступний лише адміністратору.")
        return

    text_content = message.text or message.caption or ""

    # Збереження матеріалу після підтвердження
    if any(word in text_content.lower() for word in ["все клас", "дякую", "спасибі", "super", "клас"]):
        if user.id in user_drafts:
            if user.id not in user_saved_materials:
                user_saved_materials[user.id] = []
            user_saved_materials[user.id].append(user_drafts[user.id])
            bot.send_message(chat_id, "👍 Будь ласка, босе Акіме! Твоє рішення успішно переміщено до Сховища (Управління матеріалами).")
            del user_drafts[user.id]
            if user.id in user_last_tasks:
                del user_last_tasks[user.id]
            return

    if any(word in text_content.lower() for word in ["не встр", "не так", "поправ", "правк", "зміни"]):
        if user.id in user_last_tasks:
            bot.send_message(chat_id, "🔄 Прийнято, босе! Перераховую задачу з урахуванням твоїх правок... ⏳")

    if chat_id not in user_buffers:
        user_buffers[chat_id] = []
    
    user_buffers[chat_id].append(message)
    if len(user_buffers[chat_id]) == 1:
        threading.Thread(target=process_ai_buffer, args=(chat_id, user)).start()

def process_ai_buffer(chat_id, user):
    time.sleep(BUFFER_TIME) 
    if chat_id not in user_buffers or not user_buffers[chat_id]:
        return
    
    messages_batch = user_buffers[chat_id]
    user_buffers[chat_id] = []
    bot.send_chat_action(chat_id, 'typing')

    try:
        prompt_parts = [
            "Ти — елітний AI-помічник для студента 1 курсу «Механіка і будова машин» Люблінської політехніки. "
            "Твоє завдання — детально розбирати інженерні та математичні задачі з наданих файлів або тексту. "
            "Відповідай структуровано, професійно та дружньо до боса Акіма."
        ]

        for msg in messages_batch:
            if msg.text: prompt_parts.append(f"Запит: {msg.text}")
            elif msg.caption: prompt_parts.append(f"Підпис: {msg.caption}")
            elif msg.photo:
                file_info = bot.get_file(msg.photo[-1].file_id)
                image_part = {"mime_type": "image/jpeg", "data": bot.download_file(file_info.file_path)}
                prompt_parts.append(image_part)
            elif msg.voice:
                file_info = bot.get_file(msg.voice.file_id)
                audio_part = {"mime_type": "audio/ogg", "data": bot.download_file(file_info.file_path)}
                prompt_parts.append(audio_part)

        response = ai_model.generate_content(prompt_parts)
        ai_answer = response.text
        
        user_last_tasks[user.id] = {"status": "active"}
        user_drafts[user.id] = ai_answer # Зберігаємо в чернетку для подальшого підтвердження
        
        if len(ai_answer) > 4000:
            for x in range(0, len(ai_answer), 4000): bot.send_message(chat_id, ai_answer[x:x+4000], parse_mode="Markdown")
        else:
            bot.send_message(chat_id, ai_answer, parse_mode="Markdown")

    except Exception as e:
        bot.send_message(chat_id, f"⚠️ Помилка Gemini API (можливо, невірний ключ): `{e}`", parse_mode="Markdown")

# ==========================================
# 5. РАНКОВИЙ ШЕДУЛЕР О 9:00
# ==========================================
def morning_notification_scheduler():
    while True:
        now = datetime.now()
        if now.hour == 9 and now.minute == 0:
            weather = get_lublin_weather()
            morning_msg = (
                f"☀️ **Добрий ранок, босе Акіме!**\n\n"
                f"🌡️ Погода в Любліні: **{weather}**.\n"
                f"🏛️ **Університет:** Екстрених оголошень немає.\n"
                f"⚠️ **Увага:** Наближається сесія. Якщо скоро колоквіум — кидай завдання!\n\n"
                f"☕ Сервер працює 24/7."
            )
            try: bot.send_message(ADMIN_ID, morning_msg, parse_mode="Markdown")
            except Exception: pass
            time.sleep(61)
        else:
            time.sleep(30)

threading.Thread(target=morning_notification_scheduler, daemon=True).start()

# ==========================================
# 6. БЕЗПЕЧНИЙ ЗАПУСК
# ==========================================
if __name__ == '__main__':
    print("Бот з підтримкою Gemini AI та сховищем запущено! 🚀")
    while True:
        try:
            bot.remove_webhook()
            time.sleep(1)
            bot.polling(none_stop=True, interval=1, timeout=30)
        except Exception as e:
            print(f"Помилка: {e}")
            time.sleep(3)
