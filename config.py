"""
Конфигурация бота: категории, режимы, все тексты RU/EN.
"""

CATEGORIES = {
    "any":     {"ru": "🍽 Любой рецепт",       "en": "🍽 Any Recipe",        "emoji": "🍽", "query_suffix_ru": "",                          "query_suffix_en": ""},
    "diet":    {"ru": "🥗 Диета / Похудение",   "en": "🥗 Diet / Weight Loss", "emoji": "🥗", "query_suffix_ru": "диетический похудение",    "query_suffix_en": "diet weight loss healthy"},
    "sport":   {"ru": "💪 Спортивное питание",  "en": "💪 Sport / Protein",   "emoji": "💪", "query_suffix_ru": "спорт белки протеин",       "query_suffix_en": "sport high protein fitness"},
    "dessert": {"ru": "🍰 Десерт",              "en": "🍰 Dessert",            "emoji": "🍰", "query_suffix_ru": "десерт сладкое выпечка",    "query_suffix_en": "dessert sweet baking"},
    "vegan":   {"ru": "🌱 Веганское",           "en": "🌱 Vegan",              "emoji": "🌱", "query_suffix_ru": "веганский постный",         "query_suffix_en": "vegan plant-based"},
    "quick":   {"ru": "⚡ Быстро (до 20 мин)",  "en": "⚡ Quick (20 min)",     "emoji": "⚡", "query_suffix_ru": "быстрый простой",           "query_suffix_en": "quick easy"},
    "soup":    {"ru": "🍲 Суп",                 "en": "🍲 Soup",               "emoji": "🍲", "query_suffix_ru": "суп",                       "query_suffix_en": "soup"},
    "keto":    {"ru": "🥑 Кето / Без углеводов","en": "🥑 Keto / Low Carb",   "emoji": "🥑", "query_suffix_ru": "кето без углеводов",         "query_suffix_en": "keto low carb"},
}

TEXTS = {
    "ru": {
        # Основные
        "welcome": (
            "👨‍🍳 Привет! Я <b>Шеф-бот</b> — твой личный кулинарный помощник!\n\n"
            "🥬 <b>Напиши продукты</b> через запятую, и я найду рецепты:\n"
            "<i>яйца, помидоры, сыр, лук</i>\n\n"
            "🎯 <b>Строгий режим</b> — только из твоих продуктов (без похода в магазин!)\n"
            "🥦 <b>/fridge</b> — сохрани продукты и не вводи каждый раз\n"
            "🎲 <b>/random</b> — случайный рецепт-сюрприз\n\n"
            "Выбери категорию или просто пиши продукты!"
        ),
        "help": (
            "ℹ️ <b>Как пользоваться Шеф-ботом</b>\n\n"
            "1️⃣ <b>Напиши продукты</b> через запятую:\n"
            "   <code>яйца, сыр, помидоры, лук</code>\n\n"
            "2️⃣ <b>Выбери категорию</b> — /category\n"
            "   🥗 Диета · 💪 Спорт · 🍰 Десерт · 🌱 Веган\n"
            "   ⚡ Быстро · 🍲 Суп · 🥑 Кето\n\n"
            "📌 <b>Команды:</b>\n"
            "/fridge — мой холодильник (сохранить продукты)\n"
            "/whatcook — что приготовить из холодильника\n"
            "/mode — режим поиска (обычный / строгий)\n"
            "/random — случайный рецепт\n"
            "/favorites — мои избранные рецепты\n"
            "/stats — моя статистика\n"
            "/category — категория блюда\n"
            "/help — эта справка\n\n"
            "💡 <b>Строгий режим</b> (/mode) ищет рецепты ТОЛЬКО из твоих "
            "продуктов. Соль, масло, специи и вода — не считаются!"
        ),
        "choose_category":    "🗂 Выбери категорию рецепта:",
        "category_set":       "✅ Категория: <b>{cat}</b>\n\nТеперь напиши продукты через запятую:",
        "searching":          "🔍 Ищу рецепты с: <i>{ingredients}</i>...",
        "no_results":         "😕 Рецептов не найдено.\n\n💡 Попробуй другие продукты или смени категорию — /category",
        "results_header":     "👨‍🍳 <b>Найдено рецептов: {count}</b>",
        "too_short":          "❗ Напиши хотя бы 1-2 ингредиента, например: <i>яйца, мука, молоко</i>",
        "current_category":   "📂 Текущая категория: <b>{cat}</b>",
        "error":              "⚠️ Ошибка при поиске. Попробуй позже.",
        "btn_category":       "📂 Выбрать категорию",
        # Подписи к рецепту
        "lbl_from_your":      "Из твоих продуктов",
        "lbl_buy_more":       "Докупить",
        "lbl_cooking":        "Приготовление",
        "lbl_youtube":        "Видео на YouTube",
        "lbl_full_recipe":    "Полный рецепт",
        "lbl_staples":        "Базовые (есть у всех)",
        # Режим поиска
        "mode_normal":        "🔍 Обычный поиск",
        "mode_strict":        "🎯 Только из моих продуктов",
        "choose_mode":        (
            "🔄 <b>Режим поиска</b>\n\n"
            "🔍 <b>Обычный</b> — показывает рецепты, даже если не все продукты есть\n\n"
            "🎯 <b>Строгий</b> — только рецепты из ТВОИХ продуктов\n"
            "   (соль, масло, специи не считаются — они у всех есть)"
        ),
        "mode_changed":       "✅ Режим изменён: <b>{mode}</b>",
        # Холодильник
        "fridge_contents": (
            "🥦 <b>Мой холодильник</b> ({count} продуктов):\n"
            "{items}\n\n"
            "🔄 Режим поиска: <b>{mode}</b>"
        ),
        "fridge_empty":       "🥦 Холодильник пуст.\n\nНапиши продукты через запятую, и они сохранятся автоматически!",
        "fridge_empty_cook":  "🥦 Холодильник пуст!\n\nСначала напиши продукты — они сохранятся.\nЗатем используй /whatcook",
        "fridge_cleared":     "🗑 Холодильник очищен!",
        "btn_clear_fridge":   "🗑 Очистить",
        "btn_toggle_mode":    "🔄 Сменить режим",
        "btn_whatcook":       "👨‍🍳 Что приготовить?",
        # Избранное
        "favorites_empty":    "⭐ Избранных рецептов пока нет.\n\nНажми ❤️ под рецептом, чтобы сохранить!",
        "favorites_header":   "⭐ <b>Мои избранные рецепты:</b>",
        "fav_added":          "❤️ Добавлено в избранное!",
        "fav_already":        "Уже в избранном",
        "fav_removed":        "Удалено из избранного",
        "fav_not_found":      "Рецепт не найден",
        "btn_favorite":       "❤️ В избранное",
        "btn_unfavorite":     "💔 Убрать",
        # Статистика
        "stats_text": (
            "📊 <b>Твоя статистика</b>\n\n"
            "🔍 Поисков: <b>{searches}</b>\n"
            "👁 Рецептов просмотрено: <b>{seen}</b>\n"
            "❤️ В избранном: <b>{favs}</b>\n"
            "🥦 Продуктов в холодильнике: <b>{fridge_count}</b>\n"
            "🔄 Режим поиска: <b>{mode}</b>"
        ),
        # Match
        "match_100":   "✅ Идеально — всё есть!",
        "match_high":  "✅ {pct}% совпадение — почти всё есть",
        "match_mid":   "🟡 {pct}% совпадение",
        "match_low":   "🔴 {pct}% — нужно докупить продукты",
        "strict_warn": "⚠️ В строгом режиме не нашлось идеальных рецептов. Показываю лучшее из доступного:",
        # Разное
        "random_title":  "🎲 <b>Случайный рецепт для тебя:</b>",
        "saved_fridge":  "✅ Продукты сохранены в холодильник: {items}",
    },
    "en": {
        "welcome": (
            "👨‍🍳 Hi! I'm <b>Chef Bot</b> — your personal cooking assistant!\n\n"
            "🥬 <b>Type your ingredients</b> separated by commas:\n"
            "<i>eggs, tomatoes, cheese, onion</i>\n\n"
            "🎯 <b>Strict mode</b> — recipes using ONLY what you have (no shopping needed!)\n"
            "🥦 <b>/fridge</b> — save your ingredients so you don't retype them\n"
            "🎲 <b>/random</b> — surprise recipe from your ingredients\n\n"
            "Choose a category or just type your ingredients!"
        ),
        "help": (
            "ℹ️ <b>How to use Chef Bot</b>\n\n"
            "1️⃣ <b>Type ingredients</b> separated by commas:\n"
            "   <code>eggs, cheese, tomatoes, onion</code>\n\n"
            "2️⃣ <b>Choose a category</b> — /category\n"
            "   🥗 Diet · 💪 Sport · 🍰 Dessert · 🌱 Vegan\n"
            "   ⚡ Quick · 🍲 Soup · 🥑 Keto\n\n"
            "📌 <b>Commands:</b>\n"
            "/fridge — my fridge (save ingredients)\n"
            "/whatcook — cook from my fridge\n"
            "/mode — search mode (normal / strict)\n"
            "/random — surprise recipe\n"
            "/favorites — my saved recipes\n"
            "/stats — my statistics\n"
            "/category — recipe category\n"
            "/help — this help\n\n"
            "💡 <b>Strict mode</b> (/mode) finds recipes using ONLY your ingredients. "
            "Salt, oil, spices and water don't count — everyone has those!"
        ),
        "choose_category":    "🗂 Choose a recipe category:",
        "category_set":       "✅ Category: <b>{cat}</b>\n\nNow type your ingredients separated by commas:",
        "searching":          "🔍 Searching recipes with: <i>{ingredients}</i>...",
        "no_results":         "😕 No recipes found.\n\n💡 Try different ingredients or change category — /category",
        "results_header":     "👨‍🍳 <b>Recipes found: {count}</b>",
        "too_short":          "❗ Type at least 1-2 ingredients, e.g.: <i>eggs, flour, milk</i>",
        "current_category":   "📂 Current category: <b>{cat}</b>",
        "error":              "⚠️ Search error. Please try again later.",
        "btn_category":       "📂 Choose Category",
        "lbl_from_your":      "From your ingredients",
        "lbl_buy_more":       "You'll also need",
        "lbl_cooking":        "Instructions",
        "lbl_youtube":        "Video on YouTube",
        "lbl_full_recipe":    "Full recipe",
        "lbl_staples":        "Basic staples (everyone has these)",
        "mode_normal":        "🔍 Normal search",
        "mode_strict":        "🎯 Only my ingredients",
        "choose_mode":        (
            "🔄 <b>Search Mode</b>\n\n"
            "🔍 <b>Normal</b> — shows recipes even if you're missing some ingredients\n\n"
            "🎯 <b>Strict</b> — only recipes using YOUR ingredients\n"
            "   (salt, oil, spices don't count — everyone has those)"
        ),
        "mode_changed":       "✅ Mode changed: <b>{mode}</b>",
        "fridge_contents": (
            "🥦 <b>My Fridge</b> ({count} items):\n"
            "{items}\n\n"
            "🔄 Search mode: <b>{mode}</b>"
        ),
        "fridge_empty":       "🥦 Your fridge is empty.\n\nType ingredients and they'll be saved automatically!",
        "fridge_empty_cook":  "🥦 Fridge is empty!\n\nType your ingredients first — they'll be saved.\nThen use /whatcook",
        "fridge_cleared":     "🗑 Fridge cleared!",
        "btn_clear_fridge":   "🗑 Clear",
        "btn_toggle_mode":    "🔄 Toggle mode",
        "btn_whatcook":       "👨‍🍳 What can I cook?",
        "favorites_empty":    "⭐ No favorites yet.\n\nTap ❤️ on a recipe to save it!",
        "favorites_header":   "⭐ <b>My Favorite Recipes:</b>",
        "fav_added":          "❤️ Added to favorites!",
        "fav_already":        "Already in favorites",
        "fav_removed":        "Removed from favorites",
        "fav_not_found":      "Recipe not found",
        "btn_favorite":       "❤️ Save",
        "btn_unfavorite":     "💔 Remove",
        "stats_text": (
            "📊 <b>Your Statistics</b>\n\n"
            "🔍 Searches: <b>{searches}</b>\n"
            "👁 Recipes viewed: <b>{seen}</b>\n"
            "❤️ Favorites: <b>{favs}</b>\n"
            "🥦 Fridge items: <b>{fridge_count}</b>\n"
            "🔄 Search mode: <b>{mode}</b>"
        ),
        "match_100":   "✅ Perfect match — you have everything!",
        "match_high":  "✅ {pct}% match — almost everything",
        "match_mid":   "🟡 {pct}% match",
        "match_low":   "🔴 {pct}% — missing several ingredients",
        "strict_warn": "⚠️ No perfect matches in strict mode. Showing best available:",
        "random_title":  "🎲 <b>A surprise recipe for you:</b>",
        "saved_fridge":  "✅ Saved to fridge: {items}",
    },
}
