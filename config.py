"""
Конфигурация бота: тексты, категории и эмодзи.
"""

CATEGORIES = {
    "any": {
        "ru": "🍽 Любой рецепт",
        "en": "🍽 Any Recipe",
        "emoji": "🍽",
        "query_suffix_ru": "",
        "query_suffix_en": "",
    },
    "diet": {
        "ru": "🥗 Диета / Похудение",
        "en": "🥗 Diet / Weight Loss",
        "emoji": "🥗",
        "query_suffix_ru": "диетический для похудения",
        "query_suffix_en": "diet weight loss healthy",
    },
    "sport": {
        "ru": "💪 Спортивное питание",
        "en": "💪 Sport / High Protein",
        "emoji": "💪",
        "query_suffix_ru": "спортивное питание белки",
        "query_suffix_en": "sport high protein fitness",
    },
    "dessert": {
        "ru": "🍰 Десерт",
        "en": "🍰 Dessert",
        "emoji": "🍰",
        "query_suffix_ru": "десерт сладкое выпечка",
        "query_suffix_en": "dessert sweet baking",
    },
    "vegan": {
        "ru": "🌱 Веганское",
        "en": "🌱 Vegan",
        "emoji": "🌱",
        "query_suffix_ru": "веганский постный",
        "query_suffix_en": "vegan plant-based",
    },
    "quick": {
        "ru": "⚡ Быстро (до 20 мин)",
        "en": "⚡ Quick (under 20 min)",
        "emoji": "⚡",
        "query_suffix_ru": "быстрый простой 20 минут",
        "query_suffix_en": "quick easy 20 minutes",
    },
    "soup": {
        "ru": "🍲 Суп",
        "en": "🍲 Soup",
        "emoji": "🍲",
        "query_suffix_ru": "суп",
        "query_suffix_en": "soup",
    },
    "keto": {
        "ru": "🥑 Кето / Без углеводов",
        "en": "🥑 Keto / Low Carb",
        "emoji": "🥑",
        "query_suffix_ru": "кето без углеводов",
        "query_suffix_en": "keto low carb",
    },
}

TEXTS = {
    "ru": {
        "welcome": (
            "👨‍🍳 Привет! Я <b>Шеф-бот</b> — помогу найти рецепт из твоих продуктов!\n\n"
            "📋 <b>Как пользоваться:</b>\n"
            "1️⃣ Выбери категорию — /category\n"
            "2️⃣ Напиши продукты через запятую\n"
            "   Например: <i>курица, картошка, лук, чеснок</i>\n\n"
            "🍴 Я найду рецепты специально для тебя!"
        ),
        "help": (
            "ℹ️ <b>Помощь</b>\n\n"
            "Просто напиши ингредиенты через запятую:\n"
            "<code>яйца, молоко, мука, сахар</code>\n\n"
            "📌 <b>Команды:</b>\n"
            "/start — начать заново\n"
            "/category — выбрать тип рецепта\n"
            "/help — эта справка\n\n"
            "🏷 <b>Категории:</b>\n"
            "🥗 Диета · 💪 Спорт · 🍰 Десерт\n"
            "🌱 Веган · ⚡ Быстро · 🍲 Суп · 🥑 Кето"
        ),
        "choose_category": "🗂 Выбери категорию рецепта:",
        "category_set": "✅ Категория установлена: <b>{cat}</b>\n\nТеперь напиши продукты через запятую:",
        "searching": "🔍 Ищу рецепты с: <i>{ingredients}</i>...",
        "no_results": (
            "😕 Не нашёл рецептов с этими продуктами.\n\n"
            "💡 Попробуй:\n"
            "• Написать продукты на русском\n"
            "• Убрать редкие ингредиенты\n"
            "• Сменить категорию — /category"
        ),
        "results_header": "👨‍🍳 <b>Найдено рецептов: {count}</b>\n\n",
        "recipe_item": "🍴 <b>{title}</b>\n🔗 {url}\n",
        "enter_ingredients": "📝 Напиши продукты через запятую (например: <i>курица, лук, морковь</i>):",
        "too_short": "❗ Напиши хотя бы 2 ингредиента, например: <i>яйца, мука, молоко</i>",
        "current_category": "📂 Текущая категория: <b>{cat}</b>",
        "error": "⚠️ Произошла ошибка при поиске. Попробуй позже.",
    },
    "en": {
        "welcome": (
            "👨‍🍳 Hi! I'm <b>Chef Bot</b> — I'll find recipes from your ingredients!\n\n"
            "📋 <b>How to use:</b>\n"
            "1️⃣ Choose a category — /category\n"
            "2️⃣ Type ingredients separated by commas\n"
            "   Example: <i>chicken, potato, onion, garlic</i>\n\n"
            "🍴 I'll find the best recipes for you!"
        ),
        "help": (
            "ℹ️ <b>Help</b>\n\n"
            "Just type your ingredients separated by commas:\n"
            "<code>eggs, milk, flour, sugar</code>\n\n"
            "📌 <b>Commands:</b>\n"
            "/start — restart\n"
            "/category — choose recipe type\n"
            "/help — this help\n\n"
            "🏷 <b>Categories:</b>\n"
            "🥗 Diet · 💪 Sport · 🍰 Dessert\n"
            "🌱 Vegan · ⚡ Quick · 🍲 Soup · 🥑 Keto"
        ),
        "choose_category": "🗂 Choose a recipe category:",
        "category_set": "✅ Category set: <b>{cat}</b>\n\nNow type your ingredients separated by commas:",
        "searching": "🔍 Searching recipes with: <i>{ingredients}</i>...",
        "no_results": (
            "😕 No recipes found with these ingredients.\n\n"
            "💡 Try:\n"
            "• Using more common ingredients\n"
            "• Removing rare ingredients\n"
            "• Changing category — /category"
        ),
        "results_header": "👨‍🍳 <b>Recipes found: {count}</b>\n\n",
        "recipe_item": "🍴 <b>{title}</b>\n🔗 {url}\n",
        "enter_ingredients": "📝 Type ingredients separated by commas (e.g.: <i>chicken, onion, carrot</i>):",
        "too_short": "❗ Please type at least 2 ingredients, e.g.: <i>eggs, flour, milk</i>",
        "current_category": "📂 Current category: <b>{cat}</b>",
        "error": "⚠️ An error occurred while searching. Please try again later.",
    },
}
