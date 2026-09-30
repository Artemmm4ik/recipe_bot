"""
Оптимизированный API-клиент с правильным расчетом процентов.
"""
import asyncio
import logging
import ssl
import random
from typing import Optional

import aiohttp
import certifi

from utils.pantry import is_staple

logger = logging.getLogger(__name__)

BASE = "https://www.themealdb.com/api/json/v1/1"
TIMEOUT = aiohttp.ClientTimeout(total=15, connect=8)
HEADERS = {"User-Agent": "RecipeBot/2.0"}
SSL_CTX = ssl.create_default_context(cafile=certifi.where())

CATEGORY_MAP = {
    "any":     None, "diet":    "Vegetarian", "sport":   "Chicken",
    "dessert": "Dessert", "vegan":   "Vegan", "quick":   None,
    "soup":    None, "keto":    "Beef",
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
    if data and data.get("meals"): return data["meals"][0]
    return None

async def search_by_name(session, query: str) -> list[dict]:
    data = await _get(session, f"{BASE}/search.php?s={query}")
    return data["meals"] if data and data.get("meals") else []

async def fetch_random(session) -> Optional[dict]:
    data = await _get(session, f"{BASE}/random.php")
    if data and data.get("meals"): return data["meals"][0]
    return None

def extract_ingredients_from_meal(meal: dict) -> list[str]:
    ingredients = []
    for i in range(1, 21):
        name = (meal.get(f"strIngredient{i}") or "").strip()
        measure = (meal.get(f"strMeasure{i}") or "").strip()
        if name: ingredients.append(f"{measure} {name}".strip() if measure else name)
    return ingredients


def calculate_match(meal: dict, user_ingredients_en: list[str]) -> dict:
    """
    Рассчитывает совпадение. 
    Важно: процент считается ТОЛЬКО по 'не-базовым' ингредиентам.
    Базовые (соль, масло и т.д.) исключаются из формулы, чтобы не завышать %.
    """
    recipe_ings = extract_ingredients_from_meal(meal)
    user_set = set(u.lower().strip() for u in user_ingredients_en)

    matched, missing, staples = [], [], []
    for ing in recipe_ings:
        ing_lower = ing.lower()
        if any(u in ing_lower or ing_lower.startswith(u) for u in user_set):
            matched.append(ing)
        elif is_staple(ing_lower):
            staples.append(ing)
        else:
            missing.append(ing)

    # Процент считается только по НЕ базовым продуктам!
    important_total = len(matched) + len(missing)
    if important_total > 0:
        percent = (len(matched) / important_total) * 100
    else:
        # Если рецепт состоит ТОЛЬКО из базовых продуктов (например, яичница с солью)
        percent = 100.0 if len(matched) > 0 or len(staples) > 0 else 0.0

    return {
        "percent": round(percent, 1), 
        "matched": matched, 
        "missing": missing, 
        "staples": staples, 
        "total": len(recipe_ings)
    }


def format_instructions(text: str, max_chars: int = 400) -> str:
    if not text: return ""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    res = ""
    for line in lines:
        if len(res) + len(line) > max_chars:
            res += "..."
            break
        res += line + "\n"
    return res.strip()

async def find_recipes(ingredients_en: list[str], category_key: str = "any", mode: str = "normal", max_results: int = 15) -> list[dict]:
    connector = aiohttp.TCPConnector(ssl=SSL_CTX, limit=20)
    async with aiohttp.ClientSession(connector=connector) as session:
        meal_scores: dict[str, int] = {}
        cat_meals: set[str] = set()

        cat_name = CATEGORY_MAP.get(category_key)
        if category_key == "soup":
            cr = await search_by_name(session, "soup")
            cat_meals = {m["idMeal"] for m in cr}
        elif cat_name:
            cr = await fetch_by_category(session, cat_name)
            cat_meals = {m["idMeal"] for m in cr}

        # Ищем по ВСЕМ ингредиентам параллельно
        tasks = [fetch_by_ingredient(session, ing) for ing in ingredients_en[:6]]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for r in results:
            if isinstance(r, list):
                for meal in r:
                    meal_scores[meal["idMeal"]] = meal_scores.get(meal["idMeal"], 0) + 1

        scored = [(mid, score + (10 if mid in cat_meals else 0)) for mid, score in meal_scores.items()]
        scored.sort(key=lambda x: x[1], reverse=True)
        top_25 = [mid for mid, _ in scored[:25]]

        # Перемешиваем кандидатов, чтобы при каждом запросе были РАЗНЫЕ рецепты
        random.shuffle(top_25)
        top_ids = top_25[:max_results]

        # FALLBACK: Если точных рецептов нет вообще, ищем по названиям продуктов в случайном порядке
        if not top_ids and ingredients_en:
            shuffled_ings = list(ingredients_en)
            random.shuffle(shuffled_ings)
            fb_tasks = [search_by_name(session, ing) for ing in shuffled_ings[:3]]
            fb_res = await asyncio.gather(*fb_tasks, return_exceptions=True)
            fb_meals = []
            for fr in fb_res:
                if isinstance(fr, list): fb_meals.extend(fr)
            
            random.shuffle(fb_meals)
            top_ids = [m["idMeal"] for m in fb_meals[:max_results]]

        if not top_ids and cat_meals:
            top_ids = list(cat_meals)
            random.shuffle(top_ids)
            top_ids = top_ids[:max_results]

        # Грузим детали
        detail_tasks = [fetch_meal_detail(session, mid) for mid in top_ids]
        details = await asyncio.gather(*detail_tasks, return_exceptions=True)
        full_meals = [d for d in details if isinstance(d, dict) and d]

    scored_meals = []
    for meal in full_meals:
        match = calculate_match(meal, ingredients_en)
        meal["_match"] = match
        scored_meals.append((match["percent"], meal))

    # Группируем по проценту, внутри процента — перемешиваем
    grouped = {}
    for pct, m in scored_meals:
        grouped.setdefault(pct, []).append(m)

    final_meals = []
    for pct in sorted(grouped.keys(), reverse=True):
        group = grouped[pct]
        random.shuffle(group)
        final_meals.extend(group)

    if mode == "strict":
        # В строгом режиме допускаем максимум 1 недостающий ингредиент
        filtered = [m for m in final_meals if len(m["_match"]["missing"]) <= 1 and m["_match"]["percent"] >= 50]
        if not filtered:
            filtered = final_meals
    else:
        filtered = final_meals

    return filtered

async def get_random_recipe(ingredients_en: list[str]) -> Optional[dict]:
    connector = aiohttp.TCPConnector(ssl=SSL_CTX, limit=5)
    async with aiohttp.ClientSession(connector=connector) as session:
        meal = await fetch_random(session)
        if meal: meal["_match"] = calculate_match(meal, ingredients_en)
        return meal
