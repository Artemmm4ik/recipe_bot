"""
Хендлеры холодильника: /fridge, /whatcook, /favorites, /stats, /mode.
"""
import logging

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from utils.user_state import get_user_lang_code
from utils.fridge import (
    get_fridge, save_fridge, clear_fridge, add_to_fridge,
    get_mode, set_mode, toggle_mode,
    get_favorites, remove_favorite, get_stats, inc_stat,
)
from utils.i18n import get_text
from utils.translate_text import translate_to

logger = logging.getLogger(__name__)


# ── /fridge — показать/управлять холодильником ────────────────
async def fridge_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    uid = update.effective_user.id
    lang = get_user_lang_code(uid)
    fridge = get_fridge(uid)
    mode = get_mode(uid)

    mode_label = await get_text("mode_strict" if mode == "strict" else "mode_normal", lang)

    if fridge:
        items = "\n".join(f"  • {i}" for i in fridge)
        text = (await get_text("fridge_contents", lang)).format(
            count=len(fridge), items=items, mode=mode_label
        )
    else:
        text = await get_text("fridge_empty", lang)

    keyboard = [
        [
            InlineKeyboardButton(
                await get_text("btn_clear_fridge", lang),
                callback_data="fridge_clear"
            ),
            InlineKeyboardButton(
                await get_text("btn_toggle_mode", lang),
                callback_data="fridge_toggle_mode"
            ),
        ],
        [
            InlineKeyboardButton(
                await get_text("btn_whatcook", lang),
                callback_data="fridge_cook"
            ),
        ],
    ]
    await update.message.reply_html(text, reply_markup=InlineKeyboardMarkup(keyboard))


# ── /whatcook — что приготовить из холодильника ───────────────
async def whatcook_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    uid = update.effective_user.id
    lang = get_user_lang_code(uid)
    fridge = get_fridge(uid)

    if not fridge:
        empty_msg = await get_text("fridge_empty_cook", lang)
        await update.message.reply_html(empty_msg)
        return

    # Запускаем поиск как будто пользователь ввёл продукты из холодильника
    from telegram import Message
    # Имитируем сообщение с продуктами из холодильника
    update.message.text = ", ".join(fridge)
    from handlers.recipe import recipe_message_handler
    await recipe_message_handler(update, context)


# ── /mode — переключить режим поиска ─────────────────────────
async def mode_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    uid = update.effective_user.id
    lang = get_user_lang_code(uid)
    current = get_mode(uid)

    keyboard = [
        [
            InlineKeyboardButton(
                ("✅ " if current == "normal" else "") + await get_text("mode_normal", lang),
                callback_data="mode_normal"
            ),
        ],
        [
            InlineKeyboardButton(
                ("✅ " if current == "strict" else "") + await get_text("mode_strict", lang),
                callback_data="mode_strict"
            ),
        ],
    ]
    text = await get_text("choose_mode", lang)
    await update.message.reply_html(text, reply_markup=InlineKeyboardMarkup(keyboard))


# ── /favorites — избранные рецепты ────────────────────────────
async def favorites_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    uid = update.effective_user.id
    lang = get_user_lang_code(uid)
    favs = get_favorites(uid)

    if not favs:
        msg = await get_text("favorites_empty", lang)
        await update.message.reply_html(msg)
        return

    hdr = await get_text("favorites_header", lang)
    lines = [hdr]
    for i, fav in enumerate(favs, 1):
        name = fav.get("name", "?")
        url = fav.get("url", "")
        if url:
            lines.append(f"{i}. <a href='{url}'>{name}</a>")
        else:
            lines.append(f"{i}. {name}")
    await update.message.reply_html("\n".join(lines), disable_web_page_preview=True)


# ── /stats — статистика пользователя ─────────────────────────
async def stats_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    uid = update.effective_user.id
    lang = get_user_lang_code(uid)
    stats = get_stats(uid)
    fridge = get_fridge(uid)
    mode = get_mode(uid)
    favs = get_favorites(uid)
    mode_label = await get_text("mode_strict" if mode == "strict" else "mode_normal", lang)

    text = (await get_text("stats_text", lang)).format(
        searches=stats.get("searches", 0),
        seen=stats.get("recipes_seen", 0),
        favs=len(favs),
        fridge_count=len(fridge),
        mode=mode_label,
    )
    await update.message.reply_html(text)


# ── Callback-кнопки ───────────────────────────────────────────
async def fridge_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    uid = query.from_user.id
    lang = get_user_lang_code(uid)
    data = query.data

    if data == "fridge_clear":
        clear_fridge(uid)
        msg = await get_text("fridge_cleared", lang)
        await query.edit_message_text(msg, parse_mode="HTML")

    elif data == "fridge_toggle_mode":
        new_mode = toggle_mode(uid)
        mode_label = await get_text("mode_strict" if new_mode == "strict" else "mode_normal", lang)
        msg = (await get_text("mode_changed", lang)).format(mode=mode_label)
        await query.edit_message_text(msg, parse_mode="HTML")

    elif data == "fridge_cook":
        fridge = get_fridge(uid)
        if not fridge:
            await query.edit_message_text(await get_text("fridge_empty_cook", lang), parse_mode="HTML")
        else:
            await query.edit_message_text(
                await get_text("searching", lang).then if False else
                (await get_text("searching", lang)).format(ingredients=", ".join(fridge[:5])),
                parse_mode="HTML"
            )
            # Запускаем поиск
            update.callback_query.message.text = ", ".join(fridge)
            from handlers.recipe import recipe_message_handler
            # Создаём фейковый update с текстом из холодильника
            from telegram import Message as TGMessage
            # Просто отправляем новое сообщение с инструкцией
            await query.message.reply_html(
                (await get_text("searching", lang)).format(ingredients=", ".join(fridge[:5]))
            )

    elif data in ("mode_normal", "mode_strict"):
        new_mode = data.replace("mode_", "")
        set_mode(uid, new_mode)
        mode_label = await get_text("mode_strict" if new_mode == "strict" else "mode_normal", lang)
        msg = (await get_text("mode_changed", lang)).format(mode=mode_label)
        await query.edit_message_text(msg, parse_mode="HTML")

    elif data.startswith("fav_remove_"):
        meal_id = data.replace("fav_remove_", "")
        removed = remove_favorite(uid, meal_id)
        if removed:
            msg = await get_text("fav_removed", lang)
        else:
            msg = await get_text("fav_not_found", lang)
        await query.answer(msg)

    elif data.startswith("fav_add_"):
        # Добавление в избранное из рецепта (callback из recipe.py)
        parts = data.split("|")
        meal_id = parts[0].replace("fav_add_", "")
        name = parts[1] if len(parts) > 1 else "Recipe"
        url = parts[2] if len(parts) > 2 else ""
        from utils.fridge import add_favorite
        added = add_favorite(uid, meal_id, name, url)
        if added:
            msg = await get_text("fav_added", lang)
            inc_stat(uid, "favorites_count")
        else:
            msg = await get_text("fav_already", lang)
        await query.answer(msg)
