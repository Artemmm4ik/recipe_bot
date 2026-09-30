"""
Главный обработчик сообщений с поддержкой кнопок из ReplyKeyboard.
"""
import asyncio
import logging

from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ChatAction

from config import CATEGORIES, TEXTS
from utils.user_state import get_user_lang_code, set_user_lang, get_user_category, user_data
from handlers.start import get_main_menu
from handlers.recipe import parse_ingredients, translate_ingredients_full, send_carousel_step, random_handler
from handlers.fridge import fridge_handler, favorites_handler
from utils.fridge import get_mode, set_mode, add_to_fridge, get_fridge, inc_stat
from parsers.meal_api import find_recipes

logger = logging.getLogger(__name__)

async def text_router_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Роутер текстовых сообщений: ловит кнопки меню или воспринимает текст как ингредиенты."""
    user = update.effective_user
    user_id = user.id
    text = (update.message.text or "").strip()

    if user_id not in user_data or "lang_code" not in user_data.get(user_id, {}):
        set_user_lang(user_id, (user.language_code or "ru").strip())
    
    lang_code = get_user_lang_code(user_id)
    ui_lang = "ru" if lang_code in ("ru", "uk") else "en"
    t = TEXTS[ui_lang]

    # Проверка на нажатие кнопок меню
    if text == t["btn_menu_normal"]:
        set_mode(user_id, "normal")
        await update.message.reply_html(t["mode_set_normal"])
        return
    elif text == t["btn_menu_strict"]:
        set_mode(user_id, "strict")
        await update.message.reply_html(t["mode_set_strict"])
        return
    elif text == t["btn_menu_fridge"]:
        from handlers.fridge import fridge_handler
        await fridge_handler(update, context)
        return
    elif text == t["btn_menu_fav"]:
        from handlers.fridge import favorites_handler
        await favorites_handler(update, context)
        return
    elif text == t["btn_menu_rand"]:
        from handlers.recipe import random_handler
        await random_handler(update, context)
        return
    elif text == t["btn_menu_cat"]:
        from handlers.category import category_handler
        await category_handler(update, context)
        return

    # Иначе воспринимаем текст как список продуктов
    ingredients_raw = parse_ingredients(text)
    if not ingredients_raw:
        await update.message.reply_html(t["too_short"])
        return

    add_to_fridge(user_id, ingredients_raw)
    ingredients_en = await translate_ingredients_full(ingredients_raw)

    cat_key = get_user_category(user_id)
    mode = get_mode(user_id)

    await update.message.chat.send_action(ChatAction.TYPING)
    status_msg = await update.message.reply_html(t["searching"].format(ingredients=", ".join(ingredients_raw[:5])))

    try:
        meals = await find_recipes(ingredients_en, category_key=cat_key, mode=mode, max_results=12)
    except Exception as e:
        logger.error(f"API Error: {e}")
        await status_msg.edit_text(t["error"], parse_mode="HTML")
        return

    inc_stat(user_id, "searches")

    if not meals:
        await status_msg.edit_text(t["no_results"], parse_mode="HTML")
        return

    try:
        await status_msg.delete()
    except Exception:
        pass

    if mode == "strict" and meals[0].get("_match", {}).get("percent", 0) < 80:
        await update.message.reply_html(t["strict_warn"])

    user_data.setdefault(user_id, {})["carousel"] = {"meals": meals, "idx": 0}
    await update.message.chat.send_action(ChatAction.UPLOAD_PHOTO)
    
    # Отправляем карусель
    from handlers.recipe import send_carousel_step
    await send_carousel_step(update, user_id, lang_code, t, is_edit=False)
