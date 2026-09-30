"""
Главный хендлер рецептов — с процентами совпадения, строгим режимом,
кнопками избранного и автосохранением холодильника.
"""
import logging
import re

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ChatAction
from telegram.error import TelegramError

from config import CATEGORIES, TEXTS
from utils.user_state import get_user_lang_code, set_user_lang, get_user_category, user_data
from utils.translator import translate_ingredients
from utils.translate_text import translate_to
from utils.i18n import get_text
from utils.fridge import (
    get_mode, save_fridge, get_fridge, add_to_fridge, inc_stat, add_favorite
)
from parsers.meal_api import (
    find_recipes, get_random_recipe,
    extract_ingredients_from_meal, format_instructions
)

logger = logging.getLogger(__name__)

CHOOSE_CAT_LABELS = ["выбрать категорию", "choose category"]


def parse_ingredients(text: str) -> list[str]:
    text = text.strip()
    parts = re.split(r"[,;\n]+", text)
    return [p.strip().lower() for p in parts if p.strip() and len(p.strip()) > 1]


def match_label(pct: float, lang_code: str, texts: dict) -> str:
    """Возвращает строку с оценкой совпадения."""
    if pct >= 99:
        return texts.get("match_100", "✅ 100%")
    if pct >= 80:
        return texts.get("match_high", "✅ {pct}%").format(pct=int(pct))
    if pct >= 60:
        return texts.get("match_mid", "🟡 {pct}%").format(pct=int(pct))
    return texts.get("match_low", "🔴 {pct}%").format(pct=int(pct))


async def build_caption(
    meal: dict,
    lang_code: str,
    user_ingredients_en: list[str],
) -> str:
    """Красивая подпись к фото рецепта на языке пользователя."""
    name_en   = meal.get("strMeal", "Recipe")
    area      = meal.get("strArea", "")
    category  = meal.get("strCategory", "")
    youtube   = meal.get("strYoutube", "")
    source    = meal.get("strSource", "")
    instr_raw = meal.get("strInstructions", "") or ""
    match     = meal.get("_match", {})

    is_en = lang_code.startswith("en")

    # Переводим название, категорию, область
    name    = name_en if is_en else await translate_to(name_en, lang_code)
    cat_tr  = category if is_en else await translate_to(category, lang_code)
    area_tr = area     if is_en else await translate_to(area,     lang_code)

    # Ингредиенты
    matched  = match.get("matched",  [])
    missing  = match.get("missing",  [])
    staples  = match.get("staples",  [])
    pct      = match.get("percent",  0)

    if not is_en:
        matched_tr = [await translate_to(i, lang_code) for i in matched[:8]]
        missing_tr = [await translate_to(i, lang_code) for i in missing[:5]]
    else:
        matched_tr = matched[:8]
        missing_tr = missing[:5]

    # Инструкция
    instr_short = format_instructions(instr_raw, max_chars=400)
    if instr_short and not is_en:
        instr_tr = await translate_to(instr_short, lang_code)
    else:
        instr_tr = instr_short

    # Метки
    lbl_from   = await get_text("lbl_from_your",   lang_code)
    lbl_buy    = await get_text("lbl_buy_more",    lang_code)
    lbl_cook   = await get_text("lbl_cooking",     lang_code)
    lbl_yt     = await get_text("lbl_youtube",     lang_code)
    lbl_recipe = await get_text("lbl_full_recipe", lang_code)

    # Оценка совпадения
    ui_lang = "ru" if lang_code in ("ru", "uk") else "en"
    t = TEXTS[ui_lang]
    match_str = match_label(pct, lang_code, t)

    # Собираем подпись
    caption = f"🍽 <b>{name}</b>"
    if cat_tr or area_tr:
        caption += f"\n🏷 {cat_tr}" + (f" · {area_tr}" if area_tr else "")
    caption += f"\n{match_str}\n\n"

    if matched_tr:
        caption += f"✅ <b>{lbl_from}:</b>\n"
        caption += "\n".join(f"• {i}" for i in matched_tr) + "\n"

    if missing_tr:
        caption += f"\n➕ <b>{lbl_buy}:</b>\n"
        caption += "\n".join(f"• {i}" for i in missing_tr) + "\n"

    if instr_tr:
        caption += f"\n👨‍🍳 <b>{lbl_cook}:</b>\n{instr_tr}"

    if youtube:
        caption += f"\n\n▶️ <a href='{youtube}'>{lbl_yt}</a>"
    elif source:
        caption += f"\n\n🔗 <a href='{source}'>{lbl_recipe}</a>"

    return caption[:1020] + ("..." if len(caption) > 1020 else "")


def make_recipe_keyboard(meal: dict, user_id: int, lang_code: str) -> InlineKeyboardMarkup:
    """Инлайн-кнопки под рецептом: ❤️ В избранное."""
    meal_id  = meal.get("idMeal", "")
    name     = meal.get("strMeal", "")[:50]
    source   = meal.get("strSource", "") or meal.get("strYoutube", "")
    fav_data = f"fav_add_{meal_id}|{name}|{source}"

    row = [InlineKeyboardButton("❤️", callback_data=fav_data)]
    return InlineKeyboardMarkup([row])


async def translate_ingredients_full(raw: list[str]) -> list[str]:
    """
    Переводит ингредиенты в EN: сначала словарь, потом Google для незнакомых.
    """
    from_dict = translate_ingredients(raw)
    result = []
    for orig, via_dict in zip(raw, from_dict):
        if orig == via_dict:   # словарь не нашёл — переводим через API
            en = await translate_to(orig, "en")
            result.append(en)
        else:
            result.append(via_dict)
    return result


async def recipe_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user    = update.effective_user
    user_id = user.id
    text    = update.message.text or ""

    # Язык
    if user_id not in user_data or "lang_code" not in user_data.get(user_id, {}):
        set_user_lang(user_id, (user.language_code or "ru").strip())
    lang_code = get_user_lang_code(user_id)

    # Кнопка категории
    btn_cat = (await get_text("btn_category", lang_code)).lower()
    if btn_cat in text.lower() or "/category" in text.lower():
        from handlers.category import category_handler
        await category_handler(update, context)
        return

    ingredients_raw = parse_ingredients(text)
    if not ingredients_raw:
        await update.message.reply_html(await get_text("too_short", lang_code))
        return

    # Автосохранение в холодильник
    add_to_fridge(user_id, ingredients_raw)

    # Переводим в EN для API
    ingredients_en = await translate_ingredients_full(ingredients_raw)

    cat_key  = get_user_category(user_id)
    cat_data = CATEGORIES.get(cat_key, CATEGORIES["any"])
    ui_lang  = "ru" if lang_code in ("ru", "uk") else "en"
    cat_label = cat_data[ui_lang]
    if lang_code not in ("ru", "uk") and not lang_code.startswith("en"):
        cat_label = await translate_to(cat_data["en"], lang_code)

    mode = get_mode(user_id)

    await update.message.chat.send_action(ChatAction.TYPING)
    ing_display  = ", ".join(ingredients_raw[:6])
    status_msg   = await update.message.reply_html(
        (await get_text("searching", lang_code)).format(ingredients=ing_display)
    )

    try:
        meals = await find_recipes(
            ingredients_en=ingredients_en,
            category_key=cat_key,
            mode=mode,
            max_results=3,
        )
    except Exception as e:
        logger.error(f"Ошибка API: {e}")
        await status_msg.edit_text(await get_text("error", lang_code), parse_mode="HTML")
        return

    # Статистика
    inc_stat(user_id, "searches")
    inc_stat(user_id, "recipes_seen", len(meals) if meals else 0)

    if not meals:
        await status_msg.edit_text(await get_text("no_results", lang_code), parse_mode="HTML")
        return

    try:
        await status_msg.delete()
    except TelegramError:
        pass

    # Предупреждение строгого режима
    if mode == "strict":
        best_pct = meals[0].get("_match", {}).get("percent", 0)
        if best_pct < 80:
            warn = await get_text("strict_warn", lang_code)
            await update.message.reply_html(warn)

    # Заголовок
    mode_icon = "🎯" if mode == "strict" else "🔍"
    header = (
        f"📂 <b>{cat_label}</b>  {mode_icon}\n"
        f"<i>{ing_display}</i>\n"
        f"{(await get_text('results_header', lang_code)).format(count=len(meals))}"
    )
    await update.message.reply_html(header)

    # Отправляем рецепты
    await update.message.chat.send_action(ChatAction.UPLOAD_PHOTO)
    for meal in meals:
        photo_url = meal.get("strMealThumb", "")
        caption   = await build_caption(meal, lang_code, ingredients_en)
        keyboard  = make_recipe_keyboard(meal, user_id, lang_code)

        try:
            if photo_url:
                await update.message.reply_photo(
                    photo=photo_url, caption=caption,
                    parse_mode="HTML", reply_markup=keyboard,
                )
            else:
                await update.message.reply_html(caption, reply_markup=keyboard)
        except TelegramError as e:
            logger.error(f"Ошибка отправки фото: {e}")
            try:
                await update.message.reply_html(caption, reply_markup=keyboard)
            except Exception:
                pass


# ── /random — случайный рецепт ────────────────────────────────
async def random_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id   = update.effective_user.id
    lang_code = get_user_lang_code(user_id)

    fridge = get_fridge(user_id)
    ing_en = await translate_ingredients_full(fridge) if fridge else ["chicken", "pasta", "rice"]

    await update.message.chat.send_action(ChatAction.TYPING)
    status = await update.message.reply_html(
        "🎲 " + (await get_text("searching", lang_code)).format(ingredients="...")
    )

    try:
        meal = await get_random_recipe(ing_en)
    except Exception as e:
        logger.error(f"Random error: {e}")
        await status.edit_text(await get_text("error", lang_code), parse_mode="HTML")
        return

    if not meal:
        await status.edit_text(await get_text("no_results", lang_code), parse_mode="HTML")
        return

    try:
        await status.delete()
    except TelegramError:
        pass

    title = await get_text("random_title", lang_code)
    await update.message.reply_html(title)

    caption  = await build_caption(meal, lang_code, ing_en)
    keyboard = make_recipe_keyboard(meal, user_id, lang_code)
    photo    = meal.get("strMealThumb", "")

    try:
        if photo:
            await update.message.reply_photo(
                photo=photo, caption=caption,
                parse_mode="HTML", reply_markup=keyboard,
            )
        else:
            await update.message.reply_html(caption, reply_markup=keyboard)
    except TelegramError:
        await update.message.reply_html(caption, reply_markup=keyboard)
