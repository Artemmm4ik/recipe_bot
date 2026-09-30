"""
Обработчик выбора категории: команда /category и инлайн-кнопки.
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from config import CATEGORIES, TEXTS
from utils.user_state import get_user_lang, get_user_category, set_user_category


async def category_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Показать меню выбора категории."""
    user_id = update.effective_user.id
    lang = get_user_lang(user_id)
    t = TEXTS[lang]
    current_cat = get_user_category(user_id)

    keyboard = []
    row = []
    for i, (key, data) in enumerate(CATEGORIES.items()):
        label = data[lang]
        if key == current_cat:
            label = f"✅ {label}"
        row.append(InlineKeyboardButton(label, callback_data=f"cat_{key}"))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)

    markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_html(t["choose_category"], reply_markup=markup)


async def category_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработка нажатия на кнопку категории."""
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    lang = get_user_lang(user_id)
    t = TEXTS[lang]

    cat_key = query.data.replace("cat_", "")
    if cat_key not in CATEGORIES:
        return

    set_user_category(user_id, cat_key)
    cat_name = CATEGORIES[cat_key][lang]

    await query.edit_message_text(
        t["category_set"].format(cat=cat_name),
        parse_mode="HTML",
    )
