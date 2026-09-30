"""
Главный хендлер рецептов: Карусель, Рецепт в фото, Мгновенный ответ.
"""
import asyncio
import logging
import re
import json

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import ContextTypes
from telegram.constants import ChatAction
from telegram.error import TelegramError

from config import CATEGORIES, TEXTS
from utils.user_state import get_user_lang_code, set_user_lang, get_user_category, user_data
from utils.translator import translate_ingredients
from utils.translate_text import translate_many
from utils.i18n import get_text
from utils.fridge import get_mode, add_to_fridge, get_fridge, inc_stat, is_favorite
from parsers.meal_api import (
    find_recipes, get_random_recipe,
    format_instructions,
)

logger = logging.getLogger(__name__)


def parse_ingredients(text: str) -> list[str]:
    parts = re.split(r"[,;\n]+", text.strip())
    return [p.strip().lower() for p in parts if p.strip() and len(p.strip()) > 1]


def match_label(pct: float, t: dict) -> str:
    if pct >= 99: return t["match_100"]
    if pct >= 80: return t["match_high"].format(pct=int(pct))
    if pct >= 60: return t["match_mid"]
    return t["match_low"]


async def translate_ingredients_full(raw: list[str]) -> list[str]:
    from_dict = translate_ingredients(raw)
    untr_idx = [i for i, (o, tr) in enumerate(zip(raw, from_dict)) if o == tr]
    if not untr_idx:
        return from_dict

    translated = await translate_many([raw[i] for i in untr_idx], "en")
    result = list(from_dict)
    for idx, tr in zip(untr_idx, translated):
        result[idx] = tr
    return result


async def build_single_caption(meal: dict, lang_code: str, t: dict) -> str:
    """Формирует красивую подпись, используя БАТЧИНГ перевода (1 запрос)."""
    name_en   = meal.get("strMeal", "Recipe")
    source    = meal.get("strSource", "") or meal.get("strYoutube", "")
    instr_raw = meal.get("strInstructions", "") or ""
    match     = meal.get("_match", {})
    pct       = match.get("percent", 0)

    matched = match.get("matched", [])[:6]
    missing = match.get("missing", [])[:4]

    instr_short = format_instructions(instr_raw, max_chars=400)
    is_en = lang_code.startswith("en")

    if is_en:
        name_tr    = name_en
        instr_tr   = instr_short
        matched_tr = matched
        missing_tr = missing
        lbl_have   = t["lbl_from_your"]
        lbl_need   = t["lbl_buy_more"]
        lbl_cook   = t["lbl_cooking"]
        lbl_full   = t["lbl_full_recipe"]
    else:
        # Переводим всё одним запросом через \n\n---XXX---\n\n
        to_tr = [name_en, instr_short, t["lbl_from_your"], t["lbl_buy_more"], t["lbl_cooking"], t["lbl_full_recipe"]] + matched + missing
        res = await translate_many(to_tr, lang_code)
        
        name_tr    = res[0]
        instr_tr   = res[1]
        lbl_have, lbl_need, lbl_cook, lbl_full = res[2:6]
        
        idx = 6
        matched_tr = res[idx:idx+len(matched)]; idx += len(matched)
        missing_tr = res[idx:idx+len(missing)]

    match_str = match_label(pct, t)
    
    caption = f"🍽 <b>{name_tr}</b>\n{match_str}\n\n"
    
    if matched_tr:
        caption += f"✅ <b>{lbl_have}:</b> {', '.join(matched_tr)}\n"
    if missing_tr:
        caption += f"➕ <b>{lbl_need}:</b> {', '.join(missing_tr)}\n"
        
    if instr_tr:
        caption += f"\n👨‍🍳 <b>{lbl_cook}:</b>\n{instr_tr}"

    # Ограничение Telegram 1024
    if len(caption) > 950:
        caption = caption[:950] + "..."
        
    if source:
        caption += f"\n\n🔗 <a href='{source}'>{lbl_full}</a>"
        
    return caption


def make_carousel_keyboard(meal: dict, current_idx: int, total: int, t: dict, user_id: int) -> InlineKeyboardMarkup:
    """Кнопки под рецептом с учетом статуса 'В избранном' (GUI)"""
    meal_id = meal.get("idMeal", "")
    name    = meal.get("strMeal", "")[:30]
    
    if is_favorite(user_id, meal_id):
        # Если в избранном -> кнопка 💔 Убрать
        row = [InlineKeyboardButton(f"💔 {t['btn_unfavorite']}", callback_data=f"fav_remove_{meal_id}")]
    else:
        # Если нет -> кнопка ❤️ Сохранить
        row = [InlineKeyboardButton(f"❤️ {t['btn_favorite']}", callback_data=f"fav_add_{meal_id}|{name}")]
        
    # Кнопка Следующий (если есть)
    if total > 1 and current_idx < total - 1:
        row.append(InlineKeyboardButton(t["btn_next"], callback_data="carousel_next"))
        
    return InlineKeyboardMarkup([row])


async def send_carousel_step(update_or_query, user_id: int, lang_code: str, t: dict, is_edit: bool = False) -> None:
    """Отображает текущий рецепт из карусели."""
    state = user_data.get(user_id, {}).get("carousel", {})
    meals = state.get("meals", [])
    idx   = state.get("idx", 0)
    
    if not meals or idx >= len(meals):
        msg = t["no_more_recipes"]
        if is_edit:
            await update_or_query.edit_message_text(msg, parse_mode="HTML")
        else:
            await update_or_query.message.reply_html(msg)
        return

    meal = meals[idx]
    photo_url = meal.get("strMealThumb", "")
    
    caption  = await build_single_caption(meal, lang_code, t)
    keyboard = make_carousel_keyboard(meal, idx, len(meals), t, user_id)
    
    try:
        if is_edit:
            query = update_or_query
            if photo_url:
                await query.edit_message_media(
                    media=InputMediaPhoto(photo_url, caption=caption, parse_mode="HTML"),
                    reply_markup=keyboard
                )
            else:
                await query.edit_message_text(caption, parse_mode="HTML", reply_markup=keyboard)
        else:
            message = update_or_query.message
            if photo_url:
                await message.reply_photo(photo=photo_url, caption=caption, parse_mode="HTML", reply_markup=keyboard)
            else:
                await message.reply_html(caption, reply_markup=keyboard)
    except TelegramError as e:
        logger.error(f"Carousel send error: {e}")
        try:
            if is_edit:
                await update_or_query.edit_message_text(caption, parse_mode="HTML", reply_markup=keyboard)
            else:
                await update_or_query.message.reply_html(caption, reply_markup=keyboard)
        except Exception:
            pass


async def carousel_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик кнопки ⏭ Другой рецепт."""
    query = update.callback_query
    user_id = query.from_user.id
    lang_code = get_user_lang_code(user_id)
    ui_lang   = "ru" if lang_code in ("ru", "uk") else "en"
    t         = TEXTS[ui_lang]
    
    await query.answer(t["translating"])
    
    state = user_data.setdefault(user_id, {})
    if "carousel" in state:
        state["carousel"]["idx"] += 1
        
    await send_carousel_step(query, user_id, lang_code, t, is_edit=True)


async def random_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id   = update.effective_user.id
    lang_code = get_user_lang_code(user_id)
    ui_lang   = "ru" if lang_code in ("ru", "uk") else "en"
    t         = TEXTS[ui_lang]

    fridge = get_fridge(user_id)
    ing_en = await translate_ingredients_full(fridge) if fridge else ["chicken", "pasta"]

    await update.message.chat.send_action(ChatAction.TYPING)
    status = await update.message.reply_html("🎲 " + t["searching"].format(ingredients="..."))

    try:
        meal = await get_random_recipe(ing_en)
    except Exception:
        await status.edit_text(t["error"], parse_mode="HTML")
        return

    if not meal:
        await status.edit_text(t["no_results"], parse_mode="HTML")
        return

    try:
        await status.delete()
    except TelegramError:
        pass

    user_data.setdefault(user_id, {})["carousel"] = {"meals": [meal], "idx": 0}
    await send_carousel_step(update, user_id, lang_code, t, is_edit=False)
