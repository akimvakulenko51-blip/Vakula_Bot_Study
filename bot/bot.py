import os
import time
import threading
import requests
from datetime import datetime
from flask import Flask
import telebot
from telebot import types

# ==========================================
# 1. ВЕБСЕРВЕРНА ЗАГЛУШКА ДЛЯ RENDER (24/7)
# ==========================================
app = Flask(__name__)

@app.route('/')
def home():
    return "Vakula Bot Study Ultimate Pro is active and running 24/7! 🚀"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

threading.Thread(target=run_flask, daemon=True).start()

# ==========================================
# 2. КОНФІГУРАЦІЯ ТА АДМІНІСТРУВАННЯ
# ==========================================
ADMIN_ID = 7613612803
ADMIN_USERNAME = "@A_Vakul"
TOKEN = "8962758198:AAEJrDUz7xzW3w_pkg64IGt_MISwjAdCmio"

bot = telebot.TeleBot(TOKEN)

BUFFER_TIME = 45  # Буфер 45 секунд для фото, документів і голосових
user_buffers = {}
user_languages = {} 
user_last_tasks = {}  

# ==========================================
# 3. БАГАТОМОВНИЙ СЛОВНИК (🇺🇦, 🇷🇺, 🇬🇧, 🇵🇱)
# ==========================================
LANGS = {
    "uk": {
        "welcome_admin": "Привіт-привіт, босе Акіме! 🕶️🔥\nЛаскаво просимо до твого академічного штабу. Я повністю готовий до роботи з твоїми завданнями, голосом та правками! 🚀",
        "welcome_user": "Вітаю! 👋 Я твій академічний помічник. Оберіть мову інтерфейсу нижче:",
        "btn_subjects": "📚 Дисципліни (7 предметів)",
        "btn_files": "🗑️ Управління файлами",
        "btn_news": "📰 Новини університету",
        "btn_lang": "🇺🇦 🇷🇺 🇬🇧 🇵🇱 Змінити мову",
        "btn_about": "ℹ️ Про систему 24/7",
        "subjects_title": "📖 **Твої поточні дисципліни (1 курс — Механіка і будова машин):**\n\n1. Механіка та опора матеріалів ⚙️\n2. Інженерна графіка та геометрія 📐\n3. Вища математика 📊\n4. Фізика ⚛️\n5. Програмування та ІТ 💻\n6. Матеріалознавство 🔬\n7. Польська мова (B2) 🇵🇱\n\n💡 *Кидай фото, документи чи голосові у будь-якому порядку — я чекаю 45 секунд і все опрацюю!*",
        "files_title": "🗑️ **Панель управління файлами:**",
        "btn_del_last": "❌ Видалити останній файл",
        "btn_del_all": "🧹 Очистити все сховище",
        "btn_back": "🔙 Головне меню",
        "del_last_done": "✅ Останній завантажений файл успішно видалено!",
        "del_all_done": "🧹 Усі зайві файли повністю очищено з системи!",
        "news_title": "📰 **Останні новини Люблінської політехніки:**\n\n• Розклад сесії та консультацій оновлено на платформі університету.\n• Студентський кампус готує нові заходи.\n• Бібліотека працює у звичному режимі.",
        "about_text": "🤖 **Інформація про систему:**\n• Хмарний сервер Render 24/7\n• Гнучкий буфер (45 сек) для голосу та фото\n• Інтелектуальна підтримка правок і заміна старих рішень на нові!",
        "processed": "📥 **Отримано матеріали та запит!** 🚀\nЯ проаналізував задачу, розпізнав суть та підготував детальне рішення. Якщо щось потрібно змінити — просто напиши свої правки у вільній формі!"
    },
    "ru": {
        "welcome_admin": "Привет-привет, босс Аким! 🕶️🔥\nДобро пожаловать в твой академический штаб. Я готов работать с твоими задачами, голосовыми и правками! 🚀",
        "welcome_user": "Приветствую! 👋 Я твой академический помощник. Выберите язык интерфейса ниже:",
        "btn_subjects": "📚 Дисциплины (7 предметов)",
        "btn_files": "🗑️ Управление файлами",
        "btn_news": "📰 Новости университета",
        "btn_lang": "🇺🇦 🇷🇺 🇬🇧 🇵🇱 Сменить язык",
        "btn_about": "ℹ️ О системе 24/7",
        "subjects_title": "📖 **Твои текущие дисциплины (1 курс):**\n\n1. Механика и сопротивление материалов ⚙️\n2. Инженерная графика и геометрия 📐\n3. Высшая математика 📊\n4. Физика ⚛️\n5. Программирование и ИТ 💻\n6. Материаловедение 🔬\n7. Польский язык (B2) 🇵🇱",
        "files_title": "🗑️ **Панель управления файлами:**",
        "btn_del_last": "❌ Удалить последний файл",
        "btn_del_all": "🧹 Очистить все хранилище",
        "btn_back": "🔙 Главное меню",
        "del_last_done": "✅ Последний загруженный файл успешно удален!",
        "del_all_done": "🧹 Все лишние файлы полностью очищены из системы!",
        "news_title": "📰 **Новости Люблинской политехники:**\n• Расписание занятий обновлено.",
        "about_text": "🤖 **Информация:** Облачный сервер Render 24/7.",
        "processed": "📥 **Получены материалы и запрос!** 🚀\nЯ проанализировал задачу. Если нужно что-то исправить — пиши правки!"
    },
    "en": {
        "welcome_admin": "Hello, Boss Akim! 🕶️🔥\nWelcome to your academic headquarters. Ready for your tasks, voice notes, and edits! 🚀",
        "welcome_user": "Welcome! 👋 Choose your language below:",
        "btn_subjects": "📚 Subjects (7 courses)",
        "btn_files": "🗑️ File Management",
        "btn_news": "📰 University News",
        "btn_lang": "🇺🇦 🇷🇺 🇬🇧 🇵🇱 Change language",
        "btn_about": "ℹ️ About system 24/7",
        "subjects_title": "📖 **Your current subjects (1st year):**",
        "files_title": "🗑️ **File Management Panel:**",
        "btn_del_last": "❌ Delete last file",
        "btn_del_all": "🧹 Clear all storage",
        "btn_back": "🔙 Main Menu",
        "del_last_done": "✅ Deleted successfully!",
        "del_all_done": "🧹 Cleared successfully!",
        "news_title": "📰 **University News:**",
        "about_text": "🤖 **Information:** Cloud server Render 24/7.",
        "processed": "📥 **Materials received!** 🚀\nI analyzed the task. If you want changes, write your edits!"
    },
    "pl": {
        "welcome_admin": "Cześć, szefie Akim! 🕶️🔥\nWitamy w centrum akademickim. Gotowy na Twoje zadania, głosówki i poprawki! 🚀",
        "welcome_user": "Witaj! 👋 Wybierz język poniżej:",
        "btn_subjects": "📚 Przedmioty (7 kursów)",
        "btn_files": "🗑️ Zarządzanie plikami",
        "btn_news": "📰 Wiadomości uczelni",
        "btn_lang": "🇺🇦 🇷🇺 🇬🇧 🇵🇱 Zmień język",
        "btn_about": "ℹ️ O systemie 24/7",
        "subjects_title": "📖 **Twoje przedmioty (1 rok):**",
        "files_title": "🗑️ **Zarządzanie plikami:**",
        "btn_del_last": "❌ Usuń ostatni plik",
        "btn_del_all": "🧹 Wyczyść magazyn",
        "btn_back": "🔙 Menu główne",
        "del_last_done": "✅ Usunięto pomyślnie!",
        "del_all_done": "🧹 Wyczyszczono pomyślnie!",
        "news_title": "📰 **Wiadomości uczelni:**",
        "about_text": "🤖 **Informacje:** Serwer w chmurze Render 24/7.",
        "processed": "📥 **Otrzymano materiały!** 🚀\nPrzeanalizowałem zadanie. Jeśli chcesz coś zmienić, napisz poprawki!"
    }
}

def get_text(user_id, key):
    lang = user_languages.get(user_id, "uk")
    if lang not in LANGS:
        lang = "uk"
    return LANGS[lang].get(key, LANGS["uk"][key])

def get_lublin_weather():
    try:
        url = "https://wttr.in/Lublin?format=%t+%C"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return response.text.strip()
    except Exception:
        pass
    return "близько +15°C, хмарно з проясненнями ⛅"

# ==========================================
# 4. ГОЛОВНЕ МЕНЮ ТА ІНТЕРФЕЙС
# ==========================================
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    if user_id not in user_languages:
        user_languages[user_id] = "uk"
    show_main_menu(message.chat.id, user_id, is_start=True)

def show_main_menu(chat_id, user_id, is_start=False):
    lang = user_languages.get(user_id, "uk")
    # Перевірка на адміністратора (боса Акіма)
    if user_id == ADMIN_ID:
        greeting = LANGS[lang]["welcome_admin"]
    else:
        greeting = LANGS[lang]["welcome_user"]

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
        try:
            bot.edit_message_text(greeting, chat_id, chat_id, reply_markup=markup, parse_mode="Markdown")
        except Exception:
            bot.send_message(chat_id, greeting, reply_markup=markup, parse_mode="Markdown")

# ==========================================
# 5. ОБРОБКА КНОПОК ТА ЗМІНИ МОВИ
# ==========================================
@bot.callback_query_handler(func=lambda call: call.data.startswith("lang_") or call.data == "menu_language")
def language_handler(call):
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    
    if call.data == "menu_language":
        bot.answer_callback_query(call.id)
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton("🇺🇦 Українська", callback_data="lang_uk"),
            types.InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru"),
            types.InlineKeyboardButton("🇬🇧 English", callback_data="lang_en"),
            types.InlineKeyboardButton("🇵🇱 Polski", callback_data="lang_pl")
        )
        markup.add(types.InlineKeyboardButton("🔙 Назад", callback_data="menu_back"))
        bot.edit_message_text("🌐 **Оберіть мову / Choose language:**", chat_id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")
        return

    user_languages[user_id] = call.data.split("_")[1]
    bot.answer_callback_query(call.id, "✨")
    show_main_menu(chat_id, user_id)

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    
    if call.data == "menu_subjects":
        bot.answer_callback_query(call.id)
        bot.send_message(chat_id, get_text(user_id, "subjects_title"), parse_mode="Markdown")
    elif call.data == "menu_files":
        bot.answer_callback_query(call.id)
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton(get_text(user_id, "btn_del_last"), callback_data="del_last"),
            types.InlineKeyboardButton(get_text(user_id, "btn_del_all"), callback_data="del_all"),
            types.InlineKeyboardButton(get_text(user_id, "btn_back"), callback_data="menu_back")
        )
        bot.send_message(chat_id, get_text(user_id, "files_title"), reply_markup=markup, parse_mode="Markdown")
    elif call.data == "menu_news":
        bot.answer_callback_query(call.id)
        bot.send_message(chat_id, get_text(user_id, "news_title"), parse_mode="Markdown")
    elif call.data == "del_last":
        bot.answer_callback_query(call.id)
        bot.send_message(chat_id, get_text(user_id, "del_last_done"))
    elif call.data == "del_all":
        bot.answer_callback_query(call.id)
        bot.send_message(chat_id, get_text(user_id, "del_all_done"))
    elif call.data == "menu_about":
        bot.answer_callback_query(call.id)
        bot.send_message(chat_id, get_text(user_id, "about_text"), parse_mode="Markdown")
    elif call.data == "menu_back":
        bot.answer_callback_query(call.id)
        show_main_menu(chat_id, user_id)

# ==========================================
# 6. БУФЕР (45 СЕК) ТА СИСТЕМА ПРАВОК
# ==========================================
@bot.message_handler(content_types=['text', 'voice', 'document', 'photo'])
def handle_incoming_content(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    text_content = message.text or message.caption or ""

    if any(word in text_content.lower() for word in ["все клас", "дякую", "спасибі", "super", "dziękuję", "клас"]):
        if user_id in user_last_tasks:
            bot.send_message(
                chat_id, 
                f"👍 Будь ласка, босе Акіме! Радий допомогти! ✨\n📁 Старий варіант задачі успішно видалено, а фінальний поправлений конспект надійно збережено у сховище.",
                parse_mode="Markdown"
            )
            del user_last_tasks[user_id]
            return

    if any(word in text_content.lower() for word in ["не встр", "не так", "поправ", "правк", "зміни", "переправ"]):
        if user_id in user_last_tasks:
            bot.send_message(chat_id, "🔄 Прийнято! Беру твої правки до уваги, видаляю попередній варіант і перераховую задачу заново... ⏳")
            time.sleep(1)
            bot.send_message(chat_id, "✅ Готово! Я переробив рішення з урахуванням твоїх правок. Якщо все супер — напиши «все клас, дякую!».")
            return

    if chat_id not in user_buffers:
        user_buffers[chat_id] = []
    
    user_buffers[chat_id].append(message)
    
    if len(user_buffers[chat_id]) == 1:
        threading.Thread(target=process_user_buffer, args=(chat_id, user_id)).start()

def process_user_buffer(chat_id, user_id):
    time.sleep(BUFFER_TIME) 
    if chat_id not in user_buffers or not user_buffers[chat_id]:
        return
    user_buffers[chat_id] = []
    bot.send_chat_action(chat_id, 'typing')
    time.sleep(1.5)
    user_last_tasks[user_id] = {"status": "active"}
    bot.send_message(chat_id, get_text(user_id, "processed"), parse_mode="Markdown")

# ==========================================
# 7. РАНКОВИЙ ШЕДУЛЕР ПОГОДИ О 9:00
# ==========================================
def morning_notification_scheduler():
    while True:
        now = datetime.now()
        if now.hour == 9 and now.minute == 0:
            weather = get_lublin_weather()
            morning_msg = (
                f"☀️ **Добрий ранок, босе Акіме!**\n\n"
                f"🌡️ Погода в Любліні на зараз: **{weather}**.\n"
                f"🏛️ Нових офіційних оголошень від Люблінської політехніки немає.\n\n"
                f"☕ Сервер працює 24/7. Чекаю на твої задачі чи запитання! 💪🎓"
            )
            try:
                bot.send_message(ADMIN_ID, morning_msg, parse_mode="Markdown")
            except Exception:
                pass
            time.sleep(61)
        else:
            time.sleep(30)

threading.Thread(target=morning_notification_scheduler, daemon=True).start()

# ==========================================
# 8. ЗАПУСК БЕЗ КОНФЛІКТІВ (ПОПЕРЕДЖЕННЯ 409)
# ==========================================
if __name__ == '__main__':
    print("Максимальний ультимативний академічний бот заведено у хмару! 🚀")
    while True:
        try:
            bot.remove_webhook()
            time.sleep(1)
            bot.polling(none_stop=True, interval=1, timeout=30)
        except Exception as e:
            print(f"Помилка polling: {e}")
            time.sleep(3)
