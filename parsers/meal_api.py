"""
Оптимизированный парсер с перемешиванием результатов.
"""
import asyncio
import logging
import ssl
import random
from typing import Optional

import aiohttp
import certifi

from utils.pantry import is_staple, filter_non_staples

logger = logging.getLogger(__name__)

BASE = "https://www.themealdb.com/api/json/v1/1"
TIMEOUT = aiohttp.ClientTimeout(total=15, connect=8)
HEADERS = {"User-Agent": "RecipeBot/2.0"}
SSL_CTX = ssl.create_default_context(cafile=certifi.where())

CATEGORY_MAP = {
    "any":     None,
    "diet":    "Vegetarian",
    "sport":   "Chicken",
    "dessert": "Dessert",
    "vegan":   "Vegan",
    "quick":   None,
    "soup":    None,
    "keto":    "Beef",
}


async def _get(session: aiohttp.ClientSession, url: str) -> Optional[dict]:
    try:
        async with session.get(url, headers=HEADERS, timeout=TIMEOUT) as r:
            if r.status == 200:
                return await r.json()
    except Exception as e:
        logger.warning(f"API error {url}: {e}")
    return None


async def fetch_by_ingredient(session, ingredient: str) -> list[dict]:
    data = await _get(session, f"{BASE}/filter.php?i={ingredient}")
    return data["meals"] if data and data.get("meals") else []


async def fetch_by_category(session, category: str) -> list[dict]:
    data = await _get(session, f"{BASE}/filter.php?c={category}")
    return data["meals"] if data and data.get("meals") else []


async def fetch_meal_detail(session, meal_id: str) -> Optional[dict]:
    data = await _get(session, f"{BASE}/lookup.php?i={meal_id}")
    if data and data.get("meals"):
        return data["meals"][0]
    return None


async def search_by_name(session, query: str) -> list[dict]:
    data = await _get(session, f"{BASE}/search.php?s={query}")
    return data["meals"] if data and data.get("meals") else []


async def fetch_random(session) -> Optional[dict]:
    data = await _get(session, f"{BASE}/random.php")
    if data and data.get("meals"):
        return data["meals"][0]
    return None


def extract_ingredients_from_meal(meal: dict) -> list[str]:
    ingredients = []
    for i in range(1, 21):
        name = (meal.get(f"strIngredient{i}") or "").strip()
        measure = (meal.get(f"strMeasure{i}") or "").strip()
        if name:
            ingredients.append(f"{measure} {name}".strip() if measure else name)
    return ingredients


def calculate_match(meal: dict, user_ingredients_en: list[str]) -> dict:
    recipe_ings = extract_ingredients_from_meal(meal)
    user_set = set(u.lower().strip() for u in user_ingredients_en)

    matched, missing, staples = [], [], []
    for ing in recipe_ings:
        ing_lower = ing.lower()
        has_it = any(u in ing_lower or ing_lower.startswith(u) for u in user_set)
        staple = is_staple(ing_lower)

        if has_it:
            matched.append(ing)
        elif staple:
            staples.append(ing)
        else:
            missing.append(ing)

    total = len(recipe_ings)
    covered = len(matched) + len(staples)
    percent = (covered / total * 100) if total > 0 else 0

    return {
        "percent": round(percent, 1),
        "matched": matched,
        "missing": missing,
        "staples": staples,
        "total": total,
    }


def format_instructions(text: str, max_chars: int = 550) -> str:
    if not text:
        return ""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    result = ""
    for line in lines:
        if len(result) + len(line) + 1 > max_chars:
            result += "..."
            break
        result += line + "\n"
    return result.strip()


async def find_recipes(
    ingredients_en: list[str],
    category_key: str = "any",
    mode: str = "normal",
    max_results: int = 15,  # Вытягиваем больше для разнообразия
) -> list[dict]:
    """
    Ищет рецепты, группирует по проценту совпадения и ПЕРЕМЕШИВАЕТ.
    Это дает разные результаты при каждом поиске!
    """
    connector = aiohttp.TCPConnector(ssl=SSL_CTX, limit=15)
    async with aiohttp.ClientSession(connector=connector) as session:
        meal_scores: dict[str, int] = {}
        category_meals: set[str] = set()

        cat_name = CATEGORY_MAP.get(category_key)
        if category_key == "soup":
            cat_r = await search_by_name(session, "soup")
            category_meals = {m["idMeal"] for m in cat_r}
        elif cat_name:
            cat_r = await fetch_by_category(session, cat_name)
            category_meals = {m["idMeal"] for m in cat_r}

        tasks = [fetch_by_ingredient(session, ing) for ing in ingredients_en[:5]]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for r in results:
            if isinstance(r, list):
                for meal in r:
                    mid = meal["idMeal"]
                    meal_scores[mid] = meal_scores.get(mid, 0) + 1

        if category_meals:
            scored = [
                (mid, score + (10 if mid in category_meals else 0))
                for mid, score in meal_scores.items()
            ]
        else:
            scored = list(meal_scores.items())
            
        scored.sort(key=lambda x: x[1], reverse=True)
        top_25 = [mid for mid, _ in scored[:25]]

        # ПЕРЕМЕШИВАЕМ лучших кандидатов перед загрузкой деталей!
        random.shuffle(top_25)
        top_ids = top_25[:max_results]

        if not top_ids and category_meals:
            top_ids = list(category_meals)[:max_results]
        if not top_ids and ingredients_en:
            fb = await search_by_name(session, ingredients_en[0])
            top_ids = [m["idMeal"] for m in fb[:max_results]]
            random.shuffle(top_ids)

        detail_tasks = [fetch_meal_detail(session, mid) for mid in top_ids]
        details = await asyncio.gather(*detail_tasks, return_exceptions=True)
        full_meals = [d for d in details if isinstance(d, dict) and d]

    # Считаем проценты
    scored_meals = []
    for meal in full_meals:
        match = calculate_match(meal, ingredients_en)
        meal["_match"] = match
        scored_meals.append((match["percent"], meal))

    # Сортируем по проценту, но внутри одного процента - случайно
    grouped = {}
    for pct, m in scored_meals:
        grouped.setdefault(pct, []).append(m)

    final_meals = []
    for pct in sorted(grouped.keys(), reverse=True):
        group = grouped[pct]
        random.shuffle(group)
        final_meals.extend(group)

    if mode == "strict":
        filtered = [m for m in final_meals if len(m["_match"]["missing"]) <= 2 and m["_match"]["percent"] >= 70]
        if not filtered:
            filtered = final_meals
    else:
        filtered = final_meals

    return filtered


async def get_random_recipe(ingredients_en: list[str]) -> Optional[dict]:
    connector = aiohttp.TCPConnector(ssl=SSL_CTX, limit=5)
    async with aiohttp.ClientSession(connector=connector) as session:
        meal = await fetch_random(session)
        if meal:
            meal["_match"] = calculate_match(meal, ingredients_en)
        return meal
