"""
Обработчик текстовых сообщений — поиск рецептов через TheMealDB API.
Отправляет фото блюда + подробный рецепт в подписи.
"""
import logging
import re

from telegram import Update, InputMediaPhoto
from telegram.ext import ContextTypes
from telegram.constants import ChatAction
from telegram.error import TelegramError

from config import CATEGORIES, TEXTS
from utils.user_state import get_user_lang, set_user_lang, get_user_category, user_data
from utils.translator import translate_ingredients
from parsers.meal_api import find_recipes, extract_ingredients_from_meal, format_instructions

logger = logging.getLogger(__name__)

CHOOSE_CAT_LABELS = ["выбрать категорию", "choose category"]


def parse_ingredients(text: str) -> list[str]:
    """Разбивает текст на список ингредиентов."""
    text = text.strip()
    parts = re.split(r"[,;\n]+", text)
    ingredients = []
    for p in parts:
        p = p.strip().lower()
        if p and len(p) > 1:
            ingredients.append(p)
    return ingredients


def build_caption(meal: dict, lang: str, user_ingredients_en: list[str]) -> str:
    """
    Формируем красивую подпись к фото рецепта.
    Telegram caption limit = 1024 символа.
    """
    name = meal.get("strMeal", "Рецепт")
    area = meal.get("strArea", "")
    category = meal.get("strCategory", "")
    youtube = meal.get("strYoutube", "")
    source = meal.get("strSource", "")
    instructions_raw = meal.get("strInstructions", "") or ""

    # Ингредиенты рецепта
    recipe_ings = extract_ingredients_from_meal(meal)

    # Отмечаем какие ингредиенты у пользователя уже есть
    user_set = set(i.lower() for i in user_ingredients_en)
    matched = []
    missing = []
    for ing in recipe_ings:
        ing_lower = ing.lower()
        has_it = any(u in ing_lower or ing_lower.startswith(u) for u in user_set)
        if has_it:
            matched.append(f"✅ {ing}")
        else:
            missing.append(f"➕ {ing}")

    # Инструкция — берём первые шаги
    instructions = format_instructions(instructions_raw, max_chars=400)

    if lang == "ru":
        caption = f"🍽 <b>{name}</b>"
        if area or category:
            caption += f"\n🏷 {category}" + (f" · {area}" if area else "")
        caption += "\n\n"

        if matched:
            caption += "✅ <b>Из твоих продуктов:</b>\n"
            caption += "\n".join(matched[:8]) + "\n"
        if missing:
            caption += "\n➕ <b>Докупить:</b>\n"
            caption += "\n".join(missing[:5]) + "\n"

        if instructions:
            caption += f"\n👨‍🍳 <b>Приготовление:</b>\n{instructions}"

        if youtube:
            caption += f"\n\n▶️ <a href='{youtube}'>Видео на YouTube</a>"
        elif source:
            caption += f"\n\n🔗 <a href='{source}'>Полный рецепт</a>"
    else:
        caption = f"🍽 <b>{name}</b>"
        if area or category:
            caption += f"\n🏷 {category}" + (f" · {area}" if area else "")
        caption += "\n\n"

        if matched:
            caption += "✅ <b>From your ingredients:</b>\n"
            caption += "\n".join(matched[:8]) + "\n"
        if missing:
            caption += "\n➕ <b>You'll also need:</b>\n"
            caption += "\n".join(missing[:5]) + "\n"

        if instructions:
            caption += f"\n👨‍🍳 <b>Instructions:</b>\n{instructions}"

        if youtube:
            caption += f"\n\n▶️ <a href='{youtube}'>Video on YouTube</a>"
        elif source:
            caption += f"\n\n🔗 <a href='{source}'>Full recipe</a>"

    # Обрезаем до лимита Telegram (1024 символа)
    if len(caption) > 1020:
        caption = caption[:1017] + "..."

    return caption


async def recipe_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Главный обработчик: принимает ингредиенты, отправляет фото рецептов."""
    user = update.effective_user
    user_id = user.id
    text = update.message.text or ""

    # Определяем язык
    lang = user_data.get(user_id, {}).get("lang")
    if not lang:
        tg_lang = user.language_code or "ru"
        lang = "ru" if tg_lang.startswith("ru") else "en"
        set_user_lang(user_id, lang)

    t = TEXTS[lang]

    # Кнопка "Выбрать категорию"
    if any(label in text.lower() for label in CHOOSE_CAT_LABELS):
        from handlers.category import category_handler
        await category_handler(update, context)
        return

    # Разбираем ингредиенты
    ingredients_ru = parse_ingredients(text)

    if len(ingredients_ru) < 1 or (len(ingredients_ru) == 1 and len(ingredients_ru[0]) < 3):
        await update.message.reply_html(t["too_short"])
        return

    # Переводим в английский для API
    ingredients_en = translate_ingredients(ingredients_ru)

    # Категория пользователя
    cat_key = get_user_category(user_id)
    cat_data = CATEGORIES.get(cat_key, CATEGORIES["any"])
    cat_label = cat_data[lang]

    # Показываем что ищем
    await update.message.chat.send_action(ChatAction.TYPING)
    ing_display = ", ".join(ingredients_ru[:6])
    status_msg = await update.message.reply_html(
        t["searching"].format(ingredients=ing_display)
    )

    try:
        meals = await find_recipes(
            ingredients_en=ingredients_en,
            category_key=cat_key,
            max_results=3,
        )
    except Exception as e:
        logger.error(f"Ошибка API: {e}")
        await status_msg.edit_text(t["error"], parse_mode="HTML")
        return

    if not meals:
        await status_msg.edit_text(t["no_results"], parse_mode="HTML")
        return

    # Удаляем статусное сообщение
    try:
        await status_msg.delete()
    except TelegramError:
        pass

    # Заголовок
    header = (
        f"📂 <b>{cat_label}</b>  |  "
        f"{'Найдено' if lang == 'ru' else 'Found'}: <b>{len(meals)}</b> "
        f"{'рецепта' if lang == 'ru' else 'recipes'}\n"
        f"🥬 {'Ингредиенты' if lang == 'ru' else 'Ingredients'}: <i>{ing_display}</i>"
    )
    await update.message.reply_html(header)

    # Отправляем каждый рецепт отдельным фото
    await update.message.chat.send_action(ChatAction.UPLOAD_PHOTO)
    for i, meal in enumerate(meals, 1):
        photo_url = meal.get("strMealThumb", "")
        caption = build_caption(meal, lang, ingredients_en)

        try:
            if photo_url:
                await update.message.reply_photo(
                    photo=photo_url,
                    caption=caption,
                    parse_mode="HTML",
                )
            else:
                # Если нет фото — отправляем текстом
                await update.message.reply_html(caption)
        except TelegramError as e:
            logger.error(f"Ошибка отправки фото: {e}")
            try:
                await update.message.reply_html(caption)
            except Exception:
                pass
