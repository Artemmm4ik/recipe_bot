"""
Тест парсера рецептов.
Тест 1-4: Реальный парсинг (требует интернет, работает на render.com).
Тест 5: Локальный тест HTML-парсинга (не требует сети — проверяет логику селекторов).
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from parsers.recipe_parser import search_recipes, extract_links


# ─── Локальный тест HTML-парсинга (без сети) ───────────────────
def test_html_parsing():
    print("=== Тест 5 (локальный): HTML-парсинг без сети ===")

    mock_html = """
    <html><body>
      <div class="recipe-item">
        <a href="/recipes/show/12345"><h2>Курица с картошкой в духовке</h2></a>
      </div>
      <div class="recipe-item">
        <a href="/recipes/show/67890"><h2>Жареная курица с луком</h2></a>
      </div>
      <div class="recipe-item">
        <a href="/recipes/show/11111"><h2>Картофельное пюре</h2></a>
      </div>
      <a href="/about">О нас</a>
      <a href="/login">Войти</a>
    </body></html>
    """

    results = extract_links(mock_html, "https://www.povarenok.ru", r"/recipes/show/", min_title=5)
    print(f"  Найдено ссылок на рецепты: {len(results)}")
    for r in results:
        print(f"    - {r['title'][:50]} -> {r['url'][:60]}")

    assert len(results) == 3, f"Ожидалось 3, получено {len(results)}"
    assert "Курица с картошкой в духовке" in results[0]["title"]
    print("  ✅ HTML-парсинг работает корректно!\n")


# ─── Тесты с реальной сетью ────────────────────────────────────
async def test_ru():
    print("=== Тест 1: RU — курица, картошка, лук (любой) ===")
    results = await search_recipes(
        ingredients=["курица", "картошка", "лук"],
        lang="ru", max_results=5,
    )
    print(f"  Найдено: {len(results)} рецептов")
    for r in results:
        print(f"  [{r.get('source','')}] {r['title'][:55]} | {r['url'][:65]}")
    print()


async def test_diet():
    print("=== Тест 2: RU — яйца, помидоры (диета) ===")
    results = await search_recipes(
        ingredients=["яйца", "помидоры", "огурец"],
        category_suffix_ru="диетический для похудения",
        category_suffix_en="diet weight loss",
        lang="ru", max_results=5,
    )
    print(f"  Найдено: {len(results)} рецептов")
    for r in results:
        print(f"  [{r.get('source','')}] {r['title'][:55]} | {r['url'][:65]}")
    print()


async def test_en():
    print("=== Тест 3: EN — chicken, rice, garlic ===")
    results = await search_recipes(
        ingredients=["chicken", "rice", "garlic"],
        lang="en", max_results=5,
    )
    print(f"  Найдено: {len(results)} рецептов")
    for r in results:
        print(f"  [{r.get('source','')}] {r['title'][:55]} | {r['url'][:65]}")
    print()


async def test_dessert():
    print("=== Тест 4: RU — мука, яйца, сахар (десерт) ===")
    results = await search_recipes(
        ingredients=["мука", "яйца", "сахар", "масло"],
        category_suffix_ru="десерт сладкое выпечка",
        category_suffix_en="dessert sweet baking",
        lang="ru", max_results=5,
    )
    print(f"  Найдено: {len(results)} рецептов")
    for r in results:
        print(f"  [{r.get('source','')}] {r['title'][:55]} | {r['url'][:65]}")
    print()


async def main():
    # Сначала локальный тест (не требует сети)
    test_html_parsing()

    print("📡 Сетевые тесты (требуют интернет)...")
    print("   На render.com все работают. Локально зависит от сети.\n")

    await test_ru()
    await test_diet()
    await test_en()
    await test_dessert()

    print("✅ Все тесты завершены!")


if __name__ == "__main__":
    asyncio.run(main())
