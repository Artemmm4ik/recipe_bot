"""
Обработчик текстовых сообщений — парсинг рецептов по ингредиентам.
"""
import logging
import re

from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ChatAction

from config import CATEGORIES, TEXTS
from utils.user_state import get_user_lang, set_user_lang, get_user_category
from parsers.recipe_parser import search_recipes

logger = logging.getLogger(__name__)

CHOOSE_CAT_LABELS = {
    "ru": ["📂 выбрать категорию", "категорию", "/category"],
    "en": ["📂 choose category", "category", "/category"],
}


def parse_ingredients(text: str) -> list[str]:
    """Разбивает текст на список ингредиентов."""
    text = text.strip()
    # Разбиваем по запятой, точке с запятой, переносу строки
    parts = re.split(r"[,;\n]+", text)
    ingredients = []
    for p in parts:
        p = p.strip().lower()
        if p and len(p) > 1:
            ingredients.append(p)
    return ingredients


async def recipe_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Главный обработчик текста: ищет рецепты по ингредиентам."""
    user = update.effective_user
    user_id = user.id
    text = update.message.text or ""

    # Определяем язык по первому сообщению
    from utils.user_state import get_user_lang as gul
    from langdetect import detect
    from langdetect.lang_detect_exception import LangDetectException

    try:
        detected = detect(text)
        lang = "ru" if detected == "ru" else "en"
    except LangDetectException:
        lang = "ru"

    # Если у пользователя уже установлен язык, используем его
    from utils.user_state import user_data
    if user_id in user_data and "lang" in user_data[user_id]:
        lang = user_data[user_id]["lang"]
    else:
        set_user_lang(user_id, lang)

    t = TEXTS[lang]

    # Проверяем, не нажал ли пользователь на кнопку "Выбрать категорию"
    text_lower = text.lower()
    for trigger in CHOOSE_CAT_LABELS.get(lang, []):
        if trigger in text_lower:
            from handlers.category import category_handler
            await category_handler(update, context)
            return

    # Разбираем ингредиенты
    ingredients = parse_ingredients(text)

    if len(ingredients) < 1:
        await update.message.reply_html(t["too_short"])
        return

    # Если ввели только 1 очень короткий ингредиент — подсказываем
    if len(ingredients) == 1 and len(ingredients[0]) < 4:
        await update.message.reply_html(t["too_short"])
        return

    # Получаем категорию
    cat_key = get_user_category(user_id)
    cat_data = CATEGORIES.get(cat_key, CATEGORIES["any"])

    # Показываем, что бот печатает
    await update.message.chat.send_action(ChatAction.TYPING)

    # Отправляем сообщение о поиске
    ing_display = ", ".join(ingredients[:6])
    searching_msg = await update.message.reply_html(
        t["searching"].format(ingredients=ing_display)
    )

    try:
        results = await search_recipes(
            ingredients=ingredients,
            category_suffix_ru=cat_data.get("query_suffix_ru", ""),
            category_suffix_en=cat_data.get("query_suffix_en", ""),
            lang=lang,
            max_results=8,
        )
    except Exception as e:
        logger.error(f"Ошибка поиска рецептов: {e}")
        await searching_msg.edit_text(t["error"], parse_mode="HTML")
        return

    if not results:
        await searching_msg.edit_text(t["no_results"], parse_mode="HTML")
        return

    # Формируем ответ
    cat_label = cat_data[lang]
    header = f"📂 <b>{cat_label}</b>\n" + t["results_header"].format(count=len(results))

    body = ""
    for i, recipe in enumerate(results, 1):
        title = recipe.get("title", "Без названия")
        url = recipe.get("url", "")
        source = recipe.get("source", "")
        # Ограничиваем длину названия
        if len(title) > 80:
            title = title[:77] + "..."
        body += f"{i}. <b>{title}</b>\n"
        if source:
            body += f"   📌 {source}\n"
        body += f"   🔗 {url}\n\n"

    # Разбиваем если слишком длинное
    full_text = header + body.strip()
    if len(full_text) > 4000:
        full_text = full_text[:3990] + "\n..."

    await searching_msg.edit_text(full_text, parse_mode="HTML", disable_web_page_preview=True)
