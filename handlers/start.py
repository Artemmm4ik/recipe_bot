"""
Обработчик команды /start и /help.
"""
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes

from config import TEXTS
from utils.user_state import get_user_lang, set_user_lang


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    user_id = user.id

    # Определяем язык по Telegram language_code
    tg_lang = user.language_code or "ru"
    lang = "ru" if tg_lang.startswith("ru") else "en"
    set_user_lang(user_id, lang)

    t = TEXTS[lang]
    keyboard = ReplyKeyboardMarkup(
        [[KeyboardButton("📂 Выбрать категорию" if lang == "ru" else "📂 Choose Category")]],
        resize_keyboard=True,
        one_time_keyboard=False,
    )
    await update.message.reply_html(t["welcome"], reply_markup=keyboard)


async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    lang = get_user_lang(user_id)
    t = TEXTS[lang]
    await update.message.reply_html(t["help"])
