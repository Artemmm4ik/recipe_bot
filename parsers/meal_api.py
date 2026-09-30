"""
Клиент для TheMealDB API — бесплатный, без ключей, ищет по ингредиентам.
https://www.themealdb.com/api.php
"""
import asyncio
import logging
import ssl
from typing import Optional

import aiohttp
import certifi

logger = logging.getLogger(__name__)

BASE = "https://www.themealdb.com/api/json/v1/1"
TIMEOUT = aiohttp.ClientTimeout(total=15, connect=8)
HEADERS = {"User-Agent": "RecipeBot/1.0"}

# SSL контекст — работает и на Mac, и на render.com (Linux)
SSL_CTX = ssl.create_default_context(cafile=certifi.where())

# TheMealDB категории для наших типов
CATEGORY_MAP = {
    "any":     None,
    "diet":    "Vegetarian",
    "sport":   "Chicken",
    "dessert": "Dessert",
    "vegan":   "Vegan",
    "quick":   None,
    "soup":    "Soup",   # TheMealDB не имеет категории Soup — будем искать по ключевому слову
    "keto":    "Beef",
}


async def _get(session: aiohttp.ClientSession, url: str) -> Optional[dict]:
    try:
        async with session.get(url, headers=HEADERS, timeout=TIMEOUT) as r:
            if r.status == 200:
                return await r.json()
    except Exception as e:
        logger.warning(f"TheMealDB error {url}: {e}")
    return None


async def fetch_by_ingredient(
    session: aiohttp.ClientSession, ingredient: str
) -> list[dict]:
    """Получить список блюд по одному ингредиенту."""
    url = f"{BASE}/filter.php?i={ingredient}"
    data = await _get(session, url)
    if data and data.get("meals"):
        return data["meals"]  # [{idMeal, strMeal, strMealThumb}, ...]
    return []


async def fetch_by_category(
    session: aiohttp.ClientSession, category: str
) -> list[dict]:
    """Получить список блюд по категории."""
    url = f"{BASE}/filter.php?c={category}"
    data = await _get(session, url)
    if data and data.get("meals"):
        return data["meals"]
    return []


async def fetch_meal_detail(
    session: aiohttp.ClientSession, meal_id: str
) -> Optional[dict]:
    """Получить полные данные рецепта по ID."""
    url = f"{BASE}/lookup.php?i={meal_id}"
    data = await _get(session, url)
    if data and data.get("meals"):
        return data["meals"][0]
    return None


async def search_by_name(
    session: aiohttp.ClientSession, query: str
) -> list[dict]:
    """Поиск блюд по названию (fallback)."""
    url = f"{BASE}/search.php?s={query}"
    data = await _get(session, url)
    if data and data.get("meals"):
        return data["meals"]
    return []


def extract_ingredients_from_meal(meal: dict) -> list[str]:
    """Извлечь список ингредиентов из полного рецепта."""
    ingredients = []
    for i in range(1, 21):
        name = meal.get(f"strIngredient{i}", "")
        measure = meal.get(f"strMeasure{i}", "")
        if name and name.strip():
            ingredients.append(f"{measure.strip()} {name.strip()}".strip())
    return ingredients


def format_instructions(text: str, max_chars: int = 700) -> str:
    """Обрезать инструкции до нужной длины."""
    if not text:
        return ""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    # Убираем лишние пустые строки
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    result = ""
    for line in lines:
        if len(result) + len(line) + 1 > max_chars:
            result += "\n..."
            break
        result += line + "\n"
    return result.strip()


async def find_recipes(
    ingredients_en: list[str],
    category_key: str = "any",
    max_results: int = 3,
) -> list[dict]:
    """
    Главная функция поиска.
    1. По каждому ингредиенту получаем список блюд.
    2. Считаем score (сколько ингредиентов совпало).
    3. Берём top-N блюд.
    4. Загружаем полные данные (фото, рецепт, ингредиенты).
    """
    connector = aiohttp.TCPConnector(ssl=SSL_CTX, limit=10)
    async with aiohttp.ClientSession(connector=connector) as session:

        # ── Шаг 1: собираем кандидатов ─────────────
        meal_scores: dict[str, int] = {}    # meal_id → score
        meal_info: dict[str, dict] = {}     # meal_id → {strMeal, strMealThumb}

        category_meals: set[str] = set()
        cat_name = CATEGORY_MAP.get(category_key)

        # Для категории "суп" — ищем по ключевому слову
        if category_key == "soup":
            cat_results = await search_by_name(session, "soup")
            category_meals = {m["idMeal"] for m in cat_results}
        elif cat_name:
            cat_results = await fetch_by_category(session, cat_name)
            category_meals = {m["idMeal"] for m in cat_results}
            for m in cat_results:
                meal_info[m["idMeal"]] = m

        # Ищем по каждому ингредиенту
        tasks = [fetch_by_ingredient(session, ing) for ing in ingredients_en[:6]]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for r in results:
            if isinstance(r, list):
                for meal in r:
                    mid = meal["idMeal"]
                    meal_scores[mid] = meal_scores.get(mid, 0) + 1
                    meal_info[mid] = meal

        # ── Шаг 2: фильтруем и сортируем ──────────
        if category_meals:
            # Приоритет блюдам из нужной категории
            scored = [
                (mid, score + (10 if mid in category_meals else 0))
                for mid, score in meal_scores.items()
            ]
        else:
            scored = list(meal_scores.items())

        scored.sort(key=lambda x: x[1], reverse=True)
        top_ids = [mid for mid, _ in scored[:max_results]]

        # Fallback: если ничего не нашли по ингредиентам, берём из категории
        if not top_ids and category_meals:
            top_ids = list(category_meals)[:max_results]

        # Fallback 2: если совсем ничего — ищем по первому ингредиенту по имени
        if not top_ids and ingredients_en:
            fallback = await search_by_name(session, ingredients_en[0])
            top_ids = [m["idMeal"] for m in fallback[:max_results]]
            for m in fallback:
                meal_info[m["idMeal"]] = m

        # ── Шаг 3: загружаем полные рецепты ────────
        detail_tasks = [fetch_meal_detail(session, mid) for mid in top_ids]
        details = await asyncio.gather(*detail_tasks, return_exceptions=True)

        full_meals = []
        for detail in details:
            if isinstance(detail, dict) and detail:
                full_meals.append(detail)

    return full_meals
