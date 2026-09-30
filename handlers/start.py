"""
Обработчик /start и /help — с поддержкой любого языка Telegram.
"""
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes

from utils.user_state import set_user_lang, get_user_lang_code
from utils.i18n import get_text


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    user_id = user.id

    # Читаем язык Telegram-приложения пользователя
    tg_lang = (user.language_code or "ru").strip()
    set_user_lang(user_id, tg_lang)
    lang_code = get_user_lang_code(user_id)

    welcome = await get_text("welcome", lang_code)

    # Кнопка "Выбрать категорию" — переводим
    btn_label = await get_text("btn_category", lang_code)
    keyboard = ReplyKeyboardMarkup(
        [[KeyboardButton(btn_label)]],
        resize_keyboard=True,
        one_time_keyboard=False,
    )
    await update.message.reply_html(welcome, reply_markup=keyboard)


async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    lang_code = get_user_lang_code(user_id)
    help_text = await get_text("help", lang_code)
    await update.message.reply_html(help_text)
