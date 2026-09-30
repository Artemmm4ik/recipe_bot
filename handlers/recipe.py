"""
Главный хендлер рецептов.

Ключевые оптимизации:
1. Все переводы одного рецепта — параллельно (asyncio.gather)
2. Фото с КОРОТКИМ caption (гарантированная доставка)
3. Полный рецепт — отдельным текстовым сообщением
4. Таймаут на весь перевод — не дольше 8 сек
"""
import asyncio
import logging
import re

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ChatAction
from telegram.error import TelegramError

from config import CATEGORIES, TEXTS
from utils.user_state import get_user_lang_code, set_user_lang, get_user_category, user_data
from utils.translator import translate_ingredients
from utils.translate_text import translate_to, translate_many
from utils.i18n import get_text
from utils.fridge import (
    get_mode, add_to_fridge, get_fridge, inc_stat, add_favorite
)
from parsers.meal_api import (
    find_recipes, get_random_recipe,
    extract_ingredients_from_meal, format_instructions,
)

logger = logging.getLogger(__name__)


def parse_ingredients(text: str) -> list[str]:
    parts = re.split(r"[,;\n]+", text.strip())
    return [p.strip().lower() for p in parts if p.strip() and len(p.strip()) > 1]


def match_label(pct: float, texts: dict) -> str:
    if pct >= 99:
        return texts.get("match_100", "✅ 100%")
    if pct >= 80:
        return texts.get("match_high", "✅ {pct}%").format(pct=int(pct))
    if pct >= 60:
        return texts.get("match_mid", "🟡 {pct}%").format(pct=int(pct))
    return texts.get("match_low", "🔴 {pct}%").format(pct=int(pct))


async def translate_ingredients_full(raw: list[str]) -> list[str]:
    """Словарь → Google Translate для незнакомых. Параллельно."""
    from_dict = translate_ingredients(raw)
    untranslated_idx = [i for i, (o, t) in enumerate(zip(raw, from_dict)) if o == t]

    if not untranslated_idx:
        return from_dict

    # Переводим непереведённые параллельно
    words_to_tr = [raw[i] for i in untranslated_idx]
    translated  = await translate_many(words_to_tr, "en")

    result = list(from_dict)
    for idx, tr in zip(untranslated_idx, translated):
        result[idx] = tr
    return result


async def build_short_caption(meal: dict, lang_code: str, t: dict) -> str:
    """
    КОРОТКИЙ caption для фото — только название + % совпадения.
    Переводится быстро (1 запрос), гарантированная доставка фото.
    """
    name_en = meal.get("strMeal", "Recipe")
    match   = meal.get("_match", {})
    pct     = match.get("percent", 0)

    is_en = lang_code.startswith("en")
    name  = name_en if is_en else await translate_to(name_en, lang_code)

    match_str = match_label(pct, t)
    cat = meal.get("strCategory", "")

    caption = f"🍽 <b>{name}</b>"
    if cat:
        caption += f"\n🏷 {cat}"
    caption += f"\n{match_str}"
    return caption[:900]


async def build_full_text(meal: dict, lang_code: str, user_ings_en: list[str], t: dict) -> str:
    """
    Полный рецепт как отдельное текстовое сообщение.
    Все переводы — параллельно.
    """
    name_en   = meal.get("strMeal", "Recipe")
    youtube   = meal.get("strYoutube", "")
    source    = meal.get("strSource", "")
    instr_raw = meal.get("strInstructions", "") or ""
    match     = meal.get("_match", {})

    matched  = match.get("matched",  [])[:8]
    missing  = match.get("missing",  [])[:5]
    staples  = match.get("staples",  [])[:4]

    is_en = lang_code.startswith("en")
    instr_short = format_instructions(instr_raw, max_chars=600)

    if is_en:
        # Нет переводов — мгновенно
        matched_tr = matched
        missing_tr = missing
        instr_tr   = instr_short
        lbl_from   = t.get("lbl_from_your",   "From your ingredients")
        lbl_buy    = t.get("lbl_buy_more",    "You'll also need")
        lbl_cook   = t.get("lbl_cooking",     "Instructions")
        lbl_yt     = t.get("lbl_youtube",     "Video on YouTube")
        lbl_recipe = t.get("lbl_full_recipe", "Full recipe")
        lbl_staple = t.get("lbl_staples",     "Basic staples")
    else:
        # Все переводы ПАРАЛЛЕЛЬНО
        to_translate = (
            [name_en] +
            matched +
            missing +
            [instr_short] +
            [t.get("lbl_from_your","From your ingredients"),
             t.get("lbl_buy_more","You'll also need"),
             t.get("lbl_cooking","Instructions"),
             t.get("lbl_youtube","Video on YouTube"),
             t.get("lbl_full_recipe","Full recipe"),
             t.get("lbl_staples","Basic staples")]
        )
        results = await translate_many(to_translate, lang_code)

        idx = 0
        # name_tr = results[idx]; idx += 1   # уже переведено в short caption
        idx += 1
        matched_tr = results[idx:idx+len(matched)]; idx += len(matched)
        missing_tr = results[idx:idx+len(missing)]; idx += len(missing)
        instr_tr   = results[idx]; idx += 1
        lbl_from, lbl_buy, lbl_cook, lbl_yt, lbl_recipe, lbl_staple = results[idx:idx+6]

    # Собираем текст
    lines = []
    if matched_tr:
        lines.append(f"✅ <b>{lbl_from}:</b>")
        lines += [f"• {i}" for i in matched_tr]
    if missing_tr:
        lines.append(f"\n➕ <b>{lbl_buy}:</b>")
        lines += [f"• {i}" for i in missing_tr]
    if staples:
        lines.append(f"\n🧂 <b>{lbl_staple}:</b>")
        lines.append(", ".join(staples[:4]))
    if instr_tr:
        lines.append(f"\n👨‍🍳 <b>{lbl_cook}:</b>")
        lines.append(instr_tr)
    if youtube:
        lines.append(f"\n▶️ <a href='{youtube}'>{lbl_yt}</a>")
    elif source:
        lines.append(f"\n🔗 <a href='{source}'>{lbl_recipe}</a>")

    text = "\n".join(lines)
    return text[:4000]


def make_keyboard(meal: dict) -> InlineKeyboardMarkup:
    meal_id = meal.get("idMeal", "")
    name    = meal.get("strMeal", "")[:40]
    source  = meal.get("strSource", "") or meal.get("strYoutube", "")
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("❤️", callback_data=f"fav_add_{meal_id}|{name}|{source}")
    ]])


async def send_recipe(update: Update, meal: dict, lang_code: str,
                      user_ings_en: list[str], t: dict) -> None:
    """
    Отправляем рецепт:
    1. Фото с КОРОТКИМ caption (гарантированная доставка)
    2. Полный рецепт — следующим сообщением
    """
    photo_url = meal.get("strMealThumb", "")
    keyboard  = make_keyboard(meal)

    # Короткий caption — переводим только название (1 запрос)
    short_cap = await build_short_caption(meal, lang_code, t)

    # Отправляем фото
    sent_photo = False
    if photo_url:
        try:
            await update.message.reply_photo(
                photo=photo_url,
                caption=short_cap,
                parse_mode="HTML",
            )
            sent_photo = True
        except TelegramError as e:
            logger.warning(f"reply_photo failed: {e}")

    if not sent_photo:
        # Фото не отправилось — шлём текст с названием
        try:
            await update.message.reply_html(short_cap)
        except Exception:
            pass

    # Полный рецепт — отдельным сообщением (переводим всё параллельно)
    try:
        full_text = await build_full_text(meal, lang_code, user_ings_en, t)
        if full_text:
            await update.message.reply_html(full_text, reply_markup=keyboard)
    except Exception as e:
        logger.error(f"build_full_text error: {e}")


async def recipe_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user    = update.effective_user
    user_id = user.id
    text    = update.message.text or ""

    # Язык
    if user_id not in user_data or "lang_code" not in user_data.get(user_id, {}):
        set_user_lang(user_id, (user.language_code or "ru").strip())
    lang_code = get_user_lang_code(user_id)
    ui_lang   = "ru" if lang_code in ("ru", "uk") else "en"
    t         = TEXTS[ui_lang]

    # Кнопка "Выбрать категорию"
    btn_cat = t.get("btn_category", "").lower()
    if btn_cat and btn_cat in text.lower():
        from handlers.category import category_handler
        await category_handler(update, context)
        return

    ingredients_raw = parse_ingredients(text)
    if not ingredients_raw:
        await update.message.reply_html(t["too_short"])
        return

    # Автосохранение холодильника
    add_to_fridge(user_id, ingredients_raw)

    # Перевод ингредиентов → EN (параллельно)
    ingredients_en = await translate_ingredients_full(ingredients_raw)

    cat_key  = get_user_category(user_id)
    cat_data = CATEGORIES.get(cat_key, CATEGORIES["any"])
    cat_label = cat_data[ui_lang]
    mode      = get_mode(user_id)

    # Статус
    await update.message.chat.send_action(ChatAction.TYPING)
    ing_display = ", ".join(ingredients_raw[:6])
    status_msg  = await update.message.reply_html(
        t["searching"].format(ingredients=ing_display)
    )

    # Поиск
    try:
        meals = await find_recipes(
            ingredients_en=ingredients_en,
            category_key=cat_key,
            mode=mode,
            max_results=3,
        )
    except Exception as e:
        logger.error(f"find_recipes error: {e}")
        await status_msg.edit_text(t["error"], parse_mode="HTML")
        return

    inc_stat(user_id, "searches")
    inc_stat(user_id, "recipes_seen", len(meals) if meals else 0)

    if not meals:
        await status_msg.edit_text(t["no_results"], parse_mode="HTML")
        return

    try:
        await status_msg.delete()
    except TelegramError:
        pass

    # Предупреждение строгого режима
    if mode == "strict":
        best_pct = meals[0].get("_match", {}).get("percent", 0)
        if best_pct < 80:
            await update.message.reply_html(t.get("strict_warn", ""))

    # Заголовок
    mode_icon = "🎯" if mode == "strict" else "🔍"
    header = (
        f"📂 <b>{cat_label}</b>  {mode_icon}\n"
        f"<i>{ing_display}</i>\n"
        f"{t['results_header'].format(count=len(meals))}"
    )
    await update.message.reply_html(header)

    # Отправляем рецепты
    for meal in meals:
        await update.message.chat.send_action(ChatAction.UPLOAD_PHOTO)
        await send_recipe(update, meal, lang_code, ingredients_en, t)


# ── /random ───────────────────────────────────────────────────
async def random_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id   = update.effective_user.id
    lang_code = get_user_lang_code(user_id)
    ui_lang   = "ru" if lang_code in ("ru", "uk") else "en"
    t         = TEXTS[ui_lang]

    fridge = get_fridge(user_id)
    ing_en = await translate_ingredients_full(fridge) if fridge else ["chicken", "pasta", "rice"]

    await update.message.chat.send_action(ChatAction.TYPING)
    status = await update.message.reply_html(
        "🎲 " + t["searching"].format(ingredients="...")
    )

    try:
        meal = await get_random_recipe(ing_en)
    except Exception as e:
        logger.error(f"random error: {e}")
        await status.edit_text(t["error"], parse_mode="HTML")
        return

    if not meal:
        await status.edit_text(t["no_results"], parse_mode="HTML")
        return

    try:
        await status.delete()
    except TelegramError:
        pass

    await update.message.reply_html(t.get("random_title", "🎲 <b>Рецепт-сюрприз:</b>"))
    await update.message.chat.send_action(ChatAction.UPLOAD_PHOTO)
    await send_recipe(update, meal, lang_code, ing_en, t)
