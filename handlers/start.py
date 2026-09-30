"""
Обработчик /start и /help — с ReplyKeyboard меню.
"""
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes

from utils.user_state import set_user_lang, get_user_lang_code
from config import TEXTS


def get_main_menu(lang_code: str) -> ReplyKeyboardMarkup:
    """Возвращает постоянное нижнее меню для пользователя."""
    ui_lang = "ru" if lang_code in ("ru", "uk") else "en"
    t = TEXTS[ui_lang]
    
    keyboard = [
        [KeyboardButton(t["btn_menu_normal"]), KeyboardButton(t["btn_menu_strict"])],
        [KeyboardButton(t["btn_menu_fridge"]), KeyboardButton(t["btn_menu_fav"])],
        [KeyboardButton(t["btn_menu_rand"]), KeyboardButton(t["btn_menu_cat"])],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, is_persistent=True)


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    user_id = user.id

    tg_lang = (user.language_code or "ru").strip()
    set_user_lang(user_id, tg_lang)
    lang_code = get_user_lang_code(user_id)
    ui_lang = "ru" if lang_code in ("ru", "uk") else "en"
    
    welcome = TEXTS[ui_lang]["welcome"]
    markup = get_main_menu(lang_code)
    
    await update.message.reply_html(welcome, reply_markup=markup)


async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    lang_code = get_user_lang_code(user_id)
    ui_lang = "ru" if lang_code in ("ru", "uk") else "en"
    
    help_text = TEXTS[ui_lang]["help"]
    markup = get_main_menu(lang_code)
    
    await update.message.reply_html(help_text, reply_markup=markup)
