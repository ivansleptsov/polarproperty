import os
import traceback
from dotenv import load_dotenv
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)
from telegram.error import BadRequest

# Загрузка переменных из .env
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TOKEN or not TOKEN.startswith("7691539168:"):
    raise ValueError("❌ TELEGRAM_BOT_TOKEN не найден или некорректен! Проверьте .env файл.")
CHANNEL_USERNAME = "@PolarProperty"  # Замените на ваш канал
ADMIN_ID = os.getenv("ADMIN_ID")
if ADMIN_ID:
    try:
        ADMIN_ID = int(ADMIN_ID)
    except ValueError:
        print("❌ ADMIN_ID в .env должен быть числом!")
        ADMIN_ID = None
PDF_FILE_PATH = "catalog.pdf"  # Путь к PDF файлу каталога
TEST_MODE = False  # Установите False для включения проверки подписки

# Состояния пользователей
user_state = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Главное меню"""
    photo_url = "https://images.unsplash.com/photo-1560518883-ce09059eeffa?w=800"
    text = (
        "🏠 Добро пожаловать в PolarPropertyBot!\n\n"
        "🔑 Поможем найти квартиру, дом или инвестиционный объект.\n"
        "💼 Работаем с недвижимостью по всему Тайланду.\n\n"
        "Выберите, что вас интересует:"
    )
    keyboard = [
        [InlineKeyboardButton("📂 Каталог объектов", callback_data="catalog")],
        [InlineKeyboardButton("📩 Оставить заявку", callback_data="request")],
        [InlineKeyboardButton("💬 Задать вопрос", callback_data="question")],
        [InlineKeyboardButton("📞 Контакты", callback_data="contact")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    try:
        await update.message.reply_photo(photo=photo_url, caption=text, reply_markup=reply_markup)
    except:
        await update.message.reply_text(text, reply_markup=reply_markup)

def get_back_button():
    """Кнопка возврата в главное меню"""
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад в меню", callback_data="menu")]])

async def is_user_subscribed(user_id, context):
    """Проверка подписки на канал"""
    try:
        print(f"🔍 Проверяем подписку пользователя {user_id} на канал {CHANNEL_USERNAME}")
        member = await context.bot.get_chat_member(CHANNEL_USERNAME, user_id)
        print(f"📋 Статус пользователя: {member.status}")
        is_subscribed = member.status in ["member", "administrator", "creator"]
        print(f"✅ Подписан: {is_subscribed}")
        return is_subscribed
    except BadRequest as e:
        print(f"❌ Ошибка проверки подписки: {e}")
        return False
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")
        return False

async def send_pdf_file(chat_id, context):
    """Отправка PDF файла каталога"""
    try:
        if not os.path.exists(PDF_FILE_PATH):
            print(f"❌ Файл {PDF_FILE_PATH} не найден")
            return False
            
        print(f"📤 Отправка файла {PDF_FILE_PATH} пользователю {chat_id}")
        with open(PDF_FILE_PATH, 'rb') as pdf_file:
            await context.bot.send_document(
                chat_id=chat_id,
                document=pdf_file,
                caption="📘 Каталог объектов недвижимости\n\nВ каталоге представлены лучшие предложения нашего агентства."
            )
        return True
    except Exception as e:
        print(f"❌ Ошибка при отправке PDF: {e}")
        return False

async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка нажатий кнопок"""
    query = update.callback_query
    await query.answer()

    if query.data == "catalog":
        is_subscribed = TEST_MODE or await is_user_subscribed(query.from_user.id, context)
        if is_subscribed:
            success = await send_pdf_file(query.message.chat.id, context)
            if success:
                await query.message.reply_text(
                    "✅ Каталог отправлен! Изучайте объекты и обращайтесь с вопросами.",
                    reply_markup=get_back_button()
                )
            else:
                await query.message.reply_text(
                    "⚠️ Каталог временно недоступен. Пожалуйста, попробуйте позже или обратитесь к нашим менеджерам.",
                    reply_markup=get_back_button()
                )
        else:
            keyboard = [
                [InlineKeyboardButton("📢 Подписаться на канал", url=f"https://t.me/{CHANNEL_USERNAME[1:]}")],
                [InlineKeyboardButton("✅ Проверить подписку", callback_data="catalog")],
                [InlineKeyboardButton("🔙 Назад в меню", callback_data="menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            try:
                await query.edit_message_text(
                    f"❗️ Для получения каталога подпишитесь на наш канал: {CHANNEL_USERNAME}\n\n"
                    "После подписки нажмите 'Проверить подписку'",
                    reply_markup=reply_markup
                )
            except BadRequest:
                await query.message.reply_text(
                    f"❗️ Для получения каталога подпишитесь на наш канал: {CHANNEL_USERNAME}\n\n"
                    "После подписки нажмите 'Проверить подписку'",
                    reply_markup=reply_markup
                )

    elif query.data == "contact":
        try:
            await query.edit_message_text(
                "📞 Наши контакты:\n\n"
                "👩‍💼 Директор: Любовь Данилова\n"
                "📱 Телефон: +7 (999) 123-45-67\n"
                "📨 Telegram: @lyubov_danilove\n"
                "🕒 Работаем: ПН-ПТ 9:00-18:00",
                reply_markup=get_back_button()
            )
        except BadRequest:
            await query.message.reply_text(
                "📞 Наши контакты:\n\n"
                "👩‍💼 Директор: Любовь Данилова\n"
                "📱 Телефон: +7 (999) 123-45-67\n"
                "📨 Telegram: @lyubov_danilove\n"
                "🕒 Работаем: ПН-ПТ 9:00-18:00",
                reply_markup=get_back_button()
            )

    elif query.data == "request":
        await query.message.reply_text(
            "✍️ Оставьте заявку на подбор недвижимости\n\n"
            "Укажите:\n"
            "• Ваше имя\n"
            "• Телефон\n"
            "• Город\n"
            "• Тип недвижимости\n"
            "• Бюджет\n\n"
            "Пример: Иван Петров, +7999123456, Москва, квартира 2-комн, до 15 млн"
        )
        user_state[query.from_user.id] = "request"

    elif query.data == "question":
        await query.message.reply_text(
            "💬 Задайте ваш вопрос\n\n"
            "Наши менеджеры ответят в ближайшее время. "
            "Можете спросить о любых аспектах покупки недвижимости."
        )
        user_state[query.from_user.id] = "question"

    elif query.data == "menu":
        photo_url = "https://images.unsplash.com/photo-1560518883-ce09059eeffa?w=800"
        text = "🏠 Главное меню\n\nВыберите действие:"
        keyboard = [
            [InlineKeyboardButton("📂 Каталог объектов", callback_data="catalog")],
            [InlineKeyboardButton("📩 Оставить заявку", callback_data="request")],
            [InlineKeyboardButton("💬 Задать вопрос", callback_data="question")],
            [InlineKeyboardButton("📞 Контакты", callback_data="contact")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        try:
            await query.edit_message_text(text, reply_markup=reply_markup)
        except BadRequest:
            await query.message.reply_text(text, reply_markup=reply_markup)

async def handle_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка текстовых сообщений (заявки и вопросы)"""
    user_id = update.message.from_user.id
    user_name = update.message.from_user.first_name or "Пользователь"
    username = update.message.from_user.username or "без username"
    state = user_state.get(user_id)

    if state == "request":
        request_text = update.message.text
        await update.message.reply_text(
            "✅ Заявка принята!\n\n"
            "Наш менеджер свяжется с вами в течение 30 минут.\n"
            "Спасибо за обращение!",
            reply_markup=get_back_button()
        )
        
        if ADMIN_ID:
            admin_message = (
                "📥 НОВАЯ ЗАЯВКА\n\n"
                f"👤 Пользователь: {user_name} (@{username})\n"
                f"🆔 ID: {user_id}\n"
                f"📝 Заявка: {request_text}\n"
                f"🕒 Время: {update.message.date.strftime('%d.%m.%Y %H:%M')}"
            )
            try:
                await context.bot.send_message(chat_id=ADMIN_ID, text=admin_message)
            except Exception as e:
                print(f"Не удалось отправить сообщение администратору: {ADMIN_ID}. Ошибка: {e}")

    elif state == "question":
        question_text = update.message.text
        await update.message.reply_text(
            "✅ Вопрос отправлен!\n\n"
            "Мы ответим вам в ближайшее время.\n"
            "Благодарим за интерес к нашим услугам!",
            reply_markup=get_back_button()
        )
        
        if ADMIN_ID:
            admin_message = (
                "❓ НОВЫЙ ВОПРОС\n\n"
                f"👤 Пользователь: {user_name} (@{username})\n"
                f"🆔 ID: {user_id}\n"
                f"💬 Вопрос: {question_text}\n"
                f"🕒 Время: {update.message.date.strftime('%d.%m.%Y %H:%M')}"
            )
            try:
                await context.bot.send_message(chat_id=ADMIN_ID, text=admin_message)
            except:
                print(f"Не удалось отправить вопрос администратору: {ADMIN_ID}")

    if state:
        user_state[user_id] = None

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработка ошибок"""
    print(f"Exception while handling an update: {context.error}")
    print(f"Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    # Проверяем наличие PDF файла при запуске
    if not os.path.exists(PDF_FILE_PATH):
        print(f"⚠️ Внимание: Файл {PDF_FILE_PATH} не найден! Функция каталога будет недоступна.")
        # exit()  # Можно раскомментировать, если хотите завершать работу
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_error_handler(error_handler)
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_buttons))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_messages))

    print("✅ Бот запущен")
    app.run_polling()