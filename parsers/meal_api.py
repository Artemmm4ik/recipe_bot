"""
Клиент для TheMealDB API — поиск по ингредиентам с расчётом совпадения.
"""
import asyncio
import logging
import ssl
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
    "soup":    None,   # поиск по названию
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
    """Полный список ингредиентов из рецепта."""
    ingredients = []
    for i in range(1, 21):
        name = (meal.get(f"strIngredient{i}") or "").strip()
        measure = (meal.get(f"strMeasure{i}") or "").strip()
        if name:
            ingredients.append(f"{measure} {name}".strip() if measure else name)
    return ingredients


def calculate_match(meal: dict, user_ingredients_en: list[str]) -> dict:
    """
    Рассчитывает процент совпадения рецепта с имеющимися продуктами.

    Returns:
        {
          "percent": 85.0,
          "matched": ["eggs", "tomatoes", ...],
          "missing": ["mozzarella"],    ← только НЕ-базовые
          "staples": ["olive oil", "salt"],
          "total": 10,
        }
    """
    recipe_ings = extract_ingredients_from_meal(meal)
    user_set = set(u.lower().strip() for u in user_ingredients_en)

    matched, missing, staples = [], [], []
    for ing in recipe_ings:
        ing_lower = ing.lower()
        # Проверяем: есть ли у пользователя
        has_it = any(u in ing_lower or ing_lower.startswith(u) for u in user_set)
        # Проверяем: базовый ли продукт
        staple = is_staple(ing_lower)

        if has_it:
            matched.append(ing)
        elif staple:
            staples.append(ing)
        else:
            missing.append(ing)

    # Считаем процент: (есть у юзера + базовые) / всего
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


def format_instructions(text: str, max_chars: int = 500) -> str:
    if not text:
        return ""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
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
    mode: str = "normal",          # "normal" | "strict"
    max_results: int = 3,
) -> list[dict]:
    """
    Поиск рецептов с расчётом совпадения.

    strict mode: возвращает только рецепты с match >= 80% (без учёта базовых)
    normal mode: все рецепты, сортированные по совпадению
    """
    connector = aiohttp.TCPConnector(ssl=SSL_CTX, limit=10)
    async with aiohttp.ClientSession(connector=connector) as session:

        # Шаг 1: кандидаты по ингредиентам
        meal_scores: dict[str, int] = {}
        meal_info: dict[str, dict] = {}
        category_meals: set[str] = set()

        cat_name = CATEGORY_MAP.get(category_key)
        if category_key == "soup":
            cat_r = await search_by_name(session, "soup")
            category_meals = {m["idMeal"] for m in cat_r}
        elif cat_name:
            cat_r = await fetch_by_category(session, cat_name)
            category_meals = {m["idMeal"] for m in cat_r}
            for m in cat_r:
                meal_info[m["idMeal"]] = m

        tasks = [fetch_by_ingredient(session, ing) for ing in ingredients_en[:7]]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for r in results:
            if isinstance(r, list):
                for meal in r:
                    mid = meal["idMeal"]
                    meal_scores[mid] = meal_scores.get(mid, 0) + 1
                    meal_info[mid] = meal

        # Шаг 2: сортируем кандидатов
        if category_meals:
            scored = [
                (mid, score + (10 if mid in category_meals else 0))
                for mid, score in meal_scores.items()
            ]
        else:
            scored = list(meal_scores.items())
        scored.sort(key=lambda x: x[1], reverse=True)

        # Берём топ-кандидатов для загрузки полных данных
        top_ids = [mid for mid, _ in scored[:max_results * 3]]

        # Fallbacks
        if not top_ids and category_meals:
            top_ids = list(category_meals)[:max_results * 3]
        if not top_ids and ingredients_en:
            fb = await search_by_name(session, ingredients_en[0])
            top_ids = [m["idMeal"] for m in fb[:max_results * 3]]

        # Шаг 3: загружаем полные данные
        detail_tasks = [fetch_meal_detail(session, mid) for mid in top_ids]
        details = await asyncio.gather(*detail_tasks, return_exceptions=True)

        full_meals = [d for d in details if isinstance(d, dict) and d]

    # Шаг 4: считаем match и фильтруем
    scored_meals = []
    for meal in full_meals:
        match = calculate_match(meal, ingredients_en)
        meal["_match"] = match
        scored_meals.append((match["percent"], meal))

    scored_meals.sort(key=lambda x: x[0], reverse=True)

    if mode == "strict":
        # Строгий режим: только если недостающих ≤ 2 (не считая базовых)
        filtered = [
            (pct, m) for pct, m in scored_meals
            if len(m["_match"]["missing"]) <= 2 and pct >= 70
        ]
        if not filtered:
            # Ослабляем: берём лучший по проценту
            filtered = scored_meals
    else:
        filtered = scored_meals

    return [m for _, m in filtered[:max_results]]


async def get_random_recipe(ingredients_en: list[str]) -> Optional[dict]:
    """Случайный рецепт из тех, что подходят по ингредиентам."""
    import random
    connector = aiohttp.TCPConnector(ssl=SSL_CTX, limit=5)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [fetch_by_ingredient(session, ing) for ing in ingredients_en[:3]]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        candidates = {}
        for r in results:
            if isinstance(r, list):
                for m in r:
                    candidates[m["idMeal"]] = m

        if not candidates:
            meal = await fetch_random(session)
            if meal:
                meal["_match"] = calculate_match(meal, ingredients_en)
            return meal

        # Случайный из топ-10 кандидатов
        picks = random.sample(list(candidates.keys()), min(5, len(candidates)))
        detail_tasks = [fetch_meal_detail(session, mid) for mid in picks]
        details = await asyncio.gather(*detail_tasks, return_exceptions=True)
        meals = [d for d in details if isinstance(d, dict) and d]

        if meals:
            chosen = random.choice(meals)
            chosen["_match"] = calculate_match(chosen, ingredients_en)
            return chosen
    return None
