"""
Обработчик /category — с поддержкой любого языка.
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from config import CATEGORIES
from utils.user_state import get_user_lang_code, get_user_category, set_user_category
from utils.i18n import get_text, translate_category_name


async def category_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Показать меню выбора категории."""
    user_id = update.effective_user.id
    lang_code = get_user_lang_code(user_id)
    current_cat = get_user_category(user_id)

    # Определяем base-язык для получения названий категорий
    ui_lang = "ru" if lang_code in ("ru", "uk") else "en"

    keyboard = []
    row = []
    for i, (key, data) in enumerate(CATEGORIES.items()):
        base_label = data[ui_lang]
        # Переводим если нужно
        if ui_lang == lang_code or lang_code in ("ru", "uk", "en"):
            label = base_label
        else:
            label = await translate_category_name(data["en"], lang_code)

        emoji = data["emoji"]
        if key == current_cat:
            label = f"✅ {label}"

        row.append(InlineKeyboardButton(label, callback_data=f"cat_{key}"))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)

    choose_text = await get_text("choose_category", lang_code)
    markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_html(choose_text, reply_markup=markup)


async def category_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработка нажатия на кнопку категории."""
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    lang_code = get_user_lang_code(user_id)
    ui_lang = "ru" if lang_code in ("ru", "uk") else "en"

    cat_key = query.data.replace("cat_", "")
    if cat_key not in CATEGORIES:
        return

    set_user_category(user_id, cat_key)

    # Получаем и переводим название категории
    base_name = CATEGORIES[cat_key][ui_lang]
    if lang_code not in ("ru", "uk", "en"):
        cat_name = await translate_category_name(CATEGORIES[cat_key]["en"], lang_code)
    else:
        cat_name = base_name

    cat_set_text = await get_text("category_set", lang_code)
    await query.edit_message_text(
        cat_set_text.format(cat=cat_name),
        parse_mode="HTML",
    )
