import telebot
import datetime
import os
import time
import threading
from telebot import types

TOKEN = '8962758198:AAEDwOdYh4zKx6BSaiv6KH4BscyaHbVAlko'
bot = telebot.TeleBot(TOKEN)

MY_ADMIN_USERNAME = "A_Vakul"
MY_ADMIN_ID = 7613612803

BASE_ARCHIVE = "study_archive"
if not os.path.exists(BASE_ARCHIVE):
    os.makedirs(BASE_ARCHIVE)
if not os.path.exists("voice_archive"):
    os.makedirs("voice_archive")

SUBJECTS = {
    "Matematyka": "📐 Matematyka (Вища математика)",
    "Fizyka": "⚛️ Fizyka (Фізика)",
    "Geometria": "✏️ Geometria wykreślna i zapis konstrukcji (Нарисна геометрія)",
    "Mechanika": "⚙️ Mechanika techniczna / ogólna (Технічна механіка)",
    "Materialy": "🧪 Materiały konstrukcyjne (Матеріалознавство)",
    "Technologie": "🏭 Technologie wytwarzania (Технології виробництва)",
    "Informatyka": "💻 Technologie informatyczne (Інформаційні технології)"
}

for subj_folder in SUBJECTS.keys():
    folder_path = os.path.join(BASE_ARCHIVE, subj_folder)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

LOCALIZED_TEXTS = {
    'ua': {
        'welcome': "Привіт! 👋 Це спільний навчальний архів Люблінської політехніки (Механіка і будова машин, 1 курс).\nВибери предмет нижче:",
        'empty': "📂 **{}**\n\nАрхів цього предмета поки порожній. Босс Акім скоро сюди все додасть!",
        'list': "📂 **{}** — матеріали нижче:"
    },
    'ru': {
        'welcome': "Привет! 👋 Это общий учебный архив Люблинского политехнического университета (Механика и конструирование машин, 1 курс).\nВыбери предмет ниже:",
        'empty': "📂 **{}**\n\nАрхив этого предмета пока пуст. Босс Аким скоро сюда всё добавит!",
        'list': "📂 **{}** — материалы ниже:"
    },
    'en': {
        'welcome': "Hello! 👋 This is the shared study archive of Lublin University of Technology (Mechanical Engineering, 1st year).\nChoose a subject below:",
        'empty': "📂 **{}**\n\nThis subject archive is currently empty. Boss Akim will add materials soon!",
        'list': "📂 **{}** — materials below:"
    },
    'pl': {
        'welcome': "Cześć! 👋 To wspólne archiwum dydaktyczne Politechniki Lubelskiej (Mechanika i budowa maszyn, 1 rok).\nWybierz przedmiot poniżej:",
        'empty': "📂 **{}**\n\nArchiwum tego przedmiotu jest na razie puste. Szef Akim wkrótce wszystko doda!",
        'list': "📂 **{}** — materiały poniżej:"
    }
}

user_languages = {}
photo_sessions = {}

def get_boss_greeting():
    current_hour = datetime.datetime.now().hour
    if 5 <= current_hour < 12:
        return "Добрий ранок, босс Акім! ☀️ Готовий до нових інженерних звершень."
    elif 12 <= current_hour < 18:
        return "Добрий день, босс Акім! 🌤️ Час підкорювати пари та розбирати складні задачі."
    elif 18 <= current_hour < 23:
        return "Добрий вечір, босс Акім! 🌙 Продуктивний був день, я на зв'язку для нових задач."
    else:
        return "Доброї ночі, босс Акім! 🌌 Час відпочивати, але твої матеріали та лекції в надійному місці."

def is_boss(message):
    username = message.from_user.username
    user_id = message.from_user.id
    return (username and username.lower() == MY_ADMIN_USERNAME.lower()) or (user_id == MY_ADMIN_ID)

def get_language_keyboard():
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        types.InlineKeyboardButton("🇺🇦 Українська", callback_data="lang_ua"),
        types.InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru"),
        types.InlineKeyboardButton("🇬🇧 English", callback_data="lang_en"),
        types.InlineKeyboardButton("🇵🇱 Polski", callback_data="lang_pl")
    )
    return keyboard

def get_subjects_keyboard():
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    for folder_key, folder_name in SUBJECTS.items():
        keyboard.add(types.InlineKeyboardButton(folder_name, callback_data=f"subj_{folder_key}"))
    return keyboard

def get_boss_main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(
        types.KeyboardButton("📁 Предмети та матеріали"), 
        types.KeyboardButton("📢 Новини університету"),
        types.KeyboardButton("🗑 Очистити файл / Видалити")
    )
    return markup

def detect_subject(text):
    text = text.lower()
    if any(w in text for w in ["фізик", "термодин", "оптик", "швидк", "сил"]):
        return "Fizyka"
    elif any(w in text for w in ["мат", "алгебр", "інтеграл", "похідн"]):
        return "Matematyka"
    elif any(w in text for w in ["креслен", "геометр", "проекц", "координат"]):
        return "Geometria"
    elif any(w in text for w in ["механік", "кінемат", "динамік"]):
        return "Mechanika"
    elif any(w in text for w in ["матеріал", "метал", "структур", "сплав"]):
        return "Materialy"
    elif any(w in text for w in ["технологі", "обробк", "литт", "куван"]):
        return "Technologie"
    elif any(w in text for w in ["інформат", "комп", "програм", "python"]):
        return "Informatyka"
    return "Matematyka"

@bot.message_handler(commands=["start"])
def send_welcome(message):
    if is_boss(message):
        greeting = get_boss_greeting()
        bot.reply_to(
            message, 
            f"{greeting}\n\n"
            f"⚡ **Мобільний інженерний асистент активний!**\n"
            f"Чекаю 15 секунд на твої голосові/текстові пояснення перед сортуванням фото.",
            reply_markup=get_boss_main_menu()
        )
    else:
        bot.reply_to(
            message,
            "Будь ласка, виберіть мову / Please choose your language / Wybierz język:",
            reply_markup=get_language_keyboard()
        )

@bot.callback_query_handler(func=lambda call: call.data.startswith("lang_"))
def handle_language(call):
    lang = call.data.split("_")[1]
    user_languages[call.from_user.id] = lang
    text = LOCALIZED_TEXTS[lang]['welcome']
    bot.answer_callback_query(call.id)
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=text,
        reply_markup=get_subjects_keyboard()
    )

# Коли заходимо в папку предмета — відправляємо матеріали як зручні фотографії
@bot.callback_query_handler(func=lambda call: call.data.startswith("subj_"))
def handle_subject_folder(call):
    subj_key = call.data.split("_")[1]
    folder_path = os.path.join(BASE_ARCHIVE, subj_key)
    files = os.listdir(folder_path) if os.path.exists(folder_path) else []
    
    subject_title = SUBJECTS.get(subj_key, "Матеріали")
    lang = user_languages.get(call.from_user.id, 'ua') if not is_boss(call) else 'ua'
    t = LOCALIZED_TEXTS.get(lang, LOCALIZED_TEXTS['ua'])
    
    bot.answer_callback_query(call.id)
    
    if not files:
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=t['empty'].format(subject_title),
            reply_markup=get_subjects_keyboard()
        )
    else:
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=t['list'].format(subject_title),
            reply_markup=get_subjects_keyboard()
        )
        
        # Відправляємо кожне збережене фото окремо, щоб його було зручно дивитися
        for file in files:
            file_path = os.path.join(folder_path, file)
            if os.path.isfile(file_path):
                try:
                    with open(file_path, 'rb') as photo_file:
                        bot.send_photo(call.message.chat.id, photo_file, caption=f"📄 {file}")
                except Exception:
                    pass

@bot.message_handler(func=lambda message: message.text == "📁 Предмети та матеріали")
def menu_materials(message):
    if is_boss(message):
        bot.reply_to(message, "📁 Виберіть потрібний предмет із каталогу:", reply_markup=get_subjects_keyboard())

@bot.message_handler(func=lambda message: message.text == "📢 Новини університету")
def menu_news(message):
    if is_boss(message):
        check_university_news(message)

@bot.message_handler(func=lambda message: message.text == "🗑 Очистити файл / Видалити")
def menu_delete_file(message):
    if not is_boss(message):
        return
    # Збираємо всі файли з усіх папок
    all_files = []
    for subj in SUBJECTS.keys():
        folder_path = os.path.join(BASE_ARCHIVE, subj)
        if os.path.exists(folder_path):
            for f in os.listdir(folder_path):
                all_files.append((subj, f))
                
    if not all_files:
        bot.reply_to(message, "Архів повністю порожній, нічого видаляти.")
        return
        
    file_list_str = "\n".join([f"{i+1}. [{subj}] {f}" for i, (subj, f) in enumerate(all_files)])
    bot.reply_to(message, f"🗑 **Список усіх файлів в архіві:**\n\n{file_list_str}\n\nНапиши команду у форматі: `/delete номер` (наприклад, `/delete 1`), щоб видалити непотрібний файл.")

@bot.message_handler(commands=["delete"])
def delete_specific_file(message):
    if not is_boss(message):
        return
    try:
        parts = message.text.split()
        idx = int(parts[1]) - 1
        
        all_files = []
        for subj in SUBJECTS.keys():
            folder_path = os.path.join(BASE_ARCHIVE, subj)
            if os.path.exists(folder_path):
                for f in os.listdir(folder_path):
                    all_files.append((subj, f))
                    
        if 0 <= idx < len(all_files):
            subj, fname = all_files[idx]
            file_path = os.path.join(BASE_ARCHIVE, subj, fname)
            if os.path.exists(file_path):
                os.remove(file_path)
                bot.reply_to(message, f"✅ Файл `{fname}` з папки **{subj}** успішно видалено!")
            else:
                bot.reply_to(message, "⚠️ Файл не знайдено.")
        else:
            bot.reply_to(message, "⚠️ Неправильний номер файлу.")
    except Exception:
        bot.reply_to(message, "⚠️ Використовуй правильний формат команди, наприклад: `/delete 1`")

@bot.message_handler(commands=["materials", "files"])
def show_materials(message):
    bot.reply_to(message, "📁 Каталог предметів:", reply_markup=get_subjects_keyboard())

@bot.message_handler(commands=["news", "check_news"])
def check_university_news(message):
    bot.reply_to(
        message,
        "📢 **Свіжі новини для 1 курсу (Механіка і будова машин):**\n\n"
        "1️⃣ **Конкурс проєктів:** Деканат оголосив початок реєстрації на хакатон.\n"
        "2️⃣ **Зміни у розкладі:** Лекція з термодинаміки переноситься на другу половину дня.\n"
        "3️⃣ **Бібліотека:** Доступні нові методички.\n\n"
        "🔗 *Джерело:* https://pollub.pl"
    )

@bot.message_handler(content_types=["voice"])
def handle_voice(message):
    if not is_boss(message):
        return
    chat_id = message.chat.id
    try:
        file_info = bot.get_file(message.voice.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        with open(f"voice_archive/voice_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.ogg", "wb") as f:
            f.write(downloaded_file)

        if chat_id in photo_sessions:
            photo_sessions[chat_id]["extra_input"] = True
            bot.reply_to(message, "🎧 **Голосове запитання зафіксовано!** Чекаю завершення таймера для правильного сортування...")
    except Exception:
        pass

@bot.message_handler(func=lambda message: message.chat.id in photo_sessions and message.content_type == 'text')
def handle_text_question(message):
    if not is_boss(message):
        return
    chat_id = message.chat.id
    photo_sessions[chat_id]["extra_input"] = True
    photo_sessions[chat_id]["text_question"] = message.text
    bot.reply_to(message, "💬 **Текстове пояснення прийняте!** Об'єдную з фотографіями...")

@bot.message_handler(content_types=["photo"])
def handle_photos(message):
    if not is_boss(message):
        return

    chat_id = message.chat.id
    caption = message.caption if message.caption else ""
    photo = message.photo[-1]

    if chat_id not in photo_sessions:
        photo_sessions[chat_id] = {
            "photos": [photo.file_id],
            "captions": [caption],
            "extra_input": False,
            "text_question": ""
        }
        
        bot.reply_to(message, "⏳ **Отримав фото з дошки...** Чекаю **15 секунд**, щоб ти міг надиктувати голос або написати пояснення (наприклад, що це Фізика чи Математика)...")

        def process_after_delay():
            time.sleep(15)  # Жідаємо 15 секунд для захисту від помилкового сортування
            
            session = photo_sessions.get(chat_id)
            if not session:
                return

            txt_q = session["text_question"]
            full_text = " ".join(session["captions"]) + " " + txt_q
            subject_folder = detect_subject(full_text)
            subject_name = SUBJECTS.get(subject_folder, "Матеріали")

            saved_files_count = 0
            for p_id in session["photos"]:
                try:
                    file_info = bot.get_file(p_id)
                    downloaded_file = bot.download_file(file_info.file_path)
                    
                    file_name = os.path.join(BASE_ARCHIVE, subject_folder, f"foto_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.jpg")
                    with open(file_name, "wb") as new_file:
                        new_file.write(downloaded_file)
                    saved_files_count += 1
                except Exception:
                    pass

            if chat_id in photo_sessions:
                del photo_sessions[chat_id]

            bot.send_message(
                chat_id,
                f"✅ **Успішно опрацьовано й збережено!**\n"
                f"📂 Предмет: **{subject_name}**\n"
                f"📥 Збережено фотографій: {saved_files_count} шт.\n"
                f"*(Тепер матеріали доступні у зручному форматі для тебе та групи)*"
            )

        threading.Thread(target=process_after_delay).start()
    else:
        photo_sessions[chat_id]["photos"].append(photo.file_id)
        photo_sessions[chat_id]["captions"].append(caption)
        bot.reply_to(message, "📸 Додав ще одне фото до поточного пакету розбору...")

print("Ідеальний оновлений бот із сортуванням та очищенням запущений!")
bot.infinity_polling()