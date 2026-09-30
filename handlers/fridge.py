"""
Хендлеры холодильника и интерактивного Избранного (GUI).
"""
import logging

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from utils.user_state import get_user_lang_code
from utils.fridge import (
    get_fridge, clear_fridge, get_mode, set_mode,
    get_favorites, remove_favorite, get_stats,
)
from config import TEXTS

logger = logging.getLogger(__name__)


async def fridge_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    uid = update.effective_user.id
    lang = get_user_lang_code(uid)
    ui_lang = "ru" if lang in ("ru", "uk") else "en"
    t = TEXTS[ui_lang]
    
    fridge = get_fridge(uid)

    if fridge:
        items = "\n".join(f"  • {i}" for i in fridge)
        text = t["fridge_contents"].format(items=items)
        keyboard = [[InlineKeyboardButton(t["btn_clear_fridge"], callback_data="fridge_clear")]]
        await update.message.reply_html(text, reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        text = t["fridge_empty"]
        await update.message.reply_html(text)


async def favorites_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Выводит интерактивный список избранного (GUI)."""
    uid = update.effective_user.id
    lang = get_user_lang_code(uid)
    ui_lang = "ru" if lang in ("ru", "uk") else "en"
    t = TEXTS[ui_lang]
    
    favs = get_favorites(uid)

    if not favs:
        await update.message.reply_html(t["favorites_empty"])
        return

    # Создаем GUI меню из кнопок (до 15 штук)
    keyboard = []
    for fav in favs[:15]:
        name = fav.get("name", "Recipe")
        meal_id = fav.get("id", "")
        if meal_id:
            keyboard.append([InlineKeyboardButton(f"🍽 {name}", callback_data=f"fav_show_{meal_id}")])
            
    markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_html(t["favorites_header"], reply_markup=markup)


async def stats_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    uid = update.effective_user.id
    lang = get_user_lang_code(uid)
    ui_lang = "ru" if lang in ("ru", "uk") else "en"
    t = TEXTS[ui_lang]
    
    stats = get_stats(uid)
    favs = get_favorites(uid)

    text = t["stats_text"].format(
        searches=stats.get("searches", 0),
        favs=len(favs),
    )
    await update.message.reply_html(text)


async def fridge_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    uid = query.from_user.id
    lang = get_user_lang_code(uid)
    ui_lang = "ru" if lang in ("ru", "uk") else "en"
    t = TEXTS[ui_lang]
    data = query.data

    if data == "fridge_clear":
        clear_fridge(uid)
        await query.edit_message_text(t["fridge_cleared"], parse_mode="HTML")

    elif data.startswith("fav_remove_"):
        meal_id = data.replace("fav_remove_", "")
        removed = remove_favorite(uid, meal_id)
        msg = t["fav_removed"] if removed else t["fav_not_found"]
        await query.answer(msg, show_alert=False)
        
        # Если мы кликнули на удаление прямо из карусели рецепта,
        # нужно обновить клавиатуру (поменять кнопку на "Сохранить")
        from utils.user_state import user_data
        from handlers.recipe import send_carousel_step
        if "carousel" in user_data.get(uid, {}):
            await send_carousel_step(query, uid, lang, t, is_edit=True)

    elif data.startswith("fav_add_"):
        parts = data.split("|")
        meal_id = parts[0].replace("fav_add_", "")
        name = parts[1] if len(parts) > 1 else "Recipe"
        url = parts[2] if len(parts) > 2 else ""
        from utils.fridge import add_favorite, inc_stat
        
        added = add_favorite(uid, meal_id, name, url)
        msg = t["fav_added"] if added else t["fav_already"]
        if added:
            inc_stat(uid, "favorites_count")
            
        await query.answer(msg, show_alert=False)
        
        # Обновляем клавиатуру карусели (поменяется на "Убрать")
        from utils.user_state import user_data
        from handlers.recipe import send_carousel_step
        if "carousel" in user_data.get(uid, {}):
            await send_carousel_step(query, uid, lang, t, is_edit=True)

    elif data.startswith("fav_show_"):
        # Интерактивное открытие рецепта из избранного!
        meal_id = data.replace("fav_show_", "")
        
        await query.answer(t["translating"])
        
        from parsers.meal_api import fetch_meal_detail, calculate_match, SSL_CTX
        import aiohttp
        
        connector = aiohttp.TCPConnector(ssl=SSL_CTX, limit=5)
        async with aiohttp.ClientSession(connector=connector) as session:
            meal = await fetch_meal_detail(session, meal_id)
            
        if not meal:
            await query.answer(t["error"], show_alert=True)
            return
            
        # Считаем совпадение с текущим холодильником
        fridge = get_fridge(uid)
        from handlers.recipe import translate_ingredients_full
        ing_en = await translate_ingredients_full(fridge) if fridge else []
        meal["_match"] = calculate_match(meal, ing_en)
        
        # Загружаем рецепт в "карусель" (как 1 элемент)
        from utils.user_state import user_data
        user_data.setdefault(uid, {})["carousel"] = {"meals": [meal], "idx": 0}
        
        from handlers.recipe import send_carousel_step
        # Заменяем список избранного на карточку рецепта
        await send_carousel_step(query, uid, lang, t, is_edit=True)
