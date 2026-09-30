"""
Конфигурация бота: упрощённые тексты, карусель рецептов.
"""

CATEGORIES = {
    "any":     {"ru": "🍽 Любой рецепт",       "en": "🍽 Any Recipe",        "emoji": "🍽", "query_suffix_ru": "", "query_suffix_en": ""},
    "diet":    {"ru": "🥗 Диета / Легкое",      "en": "🥗 Diet / Light",      "emoji": "🥗", "query_suffix_ru": "", "query_suffix_en": ""},
    "sport":   {"ru": "💪 Белковое",            "en": "💪 High Protein",      "emoji": "💪", "query_suffix_ru": "", "query_suffix_en": ""},
    "dessert": {"ru": "🍰 Десерт",              "en": "🍰 Dessert",            "emoji": "🍰", "query_suffix_ru": "", "query_suffix_en": ""},
    "vegan":   {"ru": "🌱 Без мяса",            "en": "🌱 Vegetarian",         "emoji": "🌱", "query_suffix_ru": "", "query_suffix_en": ""},
    "quick":   {"ru": "⚡ На скорую руку",      "en": "⚡ Quick (20 min)",     "emoji": "⚡", "query_suffix_ru": "", "query_suffix_en": ""},
    "soup":    {"ru": "🍲 Супы",                "en": "🍲 Soup",               "emoji": "🍲", "query_suffix_ru": "", "query_suffix_en": ""},
    "keto":    {"ru": "🥑 Кето",                "en": "🥑 Keto / Low Carb",   "emoji": "🥑", "query_suffix_ru": "", "query_suffix_en": ""},
}

TEXTS = {
    "ru": {
        "welcome": (
            "👋 <b>Привет! Я Шеф-бот.</b>\n"
            "Помогу приготовить вкусно из того, что есть дома.\n\n"
            "🍅 <b>Просто напиши продукты</b>, которые у тебя есть:\n"
            "<i>курица, картошка, лук, сыр</i>\n\n"
            "Я подберу рецепты, покажу чего не хватает и дам инструкцию. Начинай!"
        ),
        "help": (
            "ℹ️ <b>Как пользоваться:</b>\n\n"
            "1. Напиши продукты через запятую.\n"
            "2. Выбери рецепт (листай кнопкой ⏭).\n"
            "3. Сохраняй любимые рецепты кнопкой ❤️.\n\n"
            "<b>Команды:</b>\n"
            "/fridge — мой холодильник\n"
            "/mode — строгий поиск (только из моих продуктов)\n"
            "/favorites — сохраненные рецепты\n"
            "/category — выбрать тип блюда\n"
        ),
        "choose_category":    "🗂 Выбери категорию:",
        "category_set":       "✅ Выбрано: <b>{cat}</b>\n\nТеперь напиши свои продукты:",
        "searching":          "🍳 Ищу идеи из: <i>{ingredients}</i>...",
        "no_results":         "😕 Ничего не нашёл. Попробуй написать другие продукты или сбрось категорию.",
        "results_header":     "👨‍🍳 <b>Нашёл рецепты!</b> Листай:",
        "too_short":          "❗ Напиши хотя бы пару ингредиентов (например: <i>яйца, молоко</i>)",
        "current_category":   "📂 Текущая категория: <b>{cat}</b>",
        "error":              "⚠️ Упс, произошла ошибка сети. Попробуй ещё раз.",
        "btn_category":       "📂 Категории",
        "btn_next":           "⏭ Другой рецепт",
        "translating":        "⏳ Перевожу...",
        "no_more_recipes":    "Больше рецептов нет! Попробуй изменить продукты.",
        
        "lbl_from_your":      "Есть",
        "lbl_buy_more":       "Докупить",
        "lbl_cooking":        "Рецепт",
        "lbl_full_recipe":    "Читать полностью",
        
        "mode_normal":        "🔍 Обычный поиск",
        "mode_strict":        "🎯 Только из моих продуктов",
        "choose_mode":        "🔄 <b>Режим поиска</b>\n\n🔍 Обычный — показывает больше рецептов.\n🎯 Строгий — только из того, что есть (без похода в магазин).",
        "mode_changed":       "✅ Режим изменён: <b>{mode}</b>",
        
        "fridge_contents":    "🥦 <b>Мой холодильник:</b>\n{items}\n\nНажми «Что приготовить», и я найду рецепт!",
        "fridge_empty":       "🥦 Холодильник пуст. Напиши продукты, и они сохранятся!",
        "fridge_empty_cook":  "Сначала напиши продукты в чат!",
        "fridge_cleared":     "🗑 Очищено!",
        "btn_clear_fridge":   "🗑 Очистить",
        "btn_toggle_mode":    "🔄 Режим: {mode}",
        "btn_whatcook":       "👨‍🍳 Что приготовить?",
        
        "favorites_empty":    "⭐ Нет сохраненных рецептов.",
        "favorites_header":   "⭐ <b>Любимые рецепты:</b>",
        "fav_added":          "❤️ Сохранено!",
        "fav_already":        "Уже сохранено",
        "fav_removed":        "Удалено",
        "fav_not_found":      "Не найдено",
        
        "stats_text":         "📊 <b>Статистика:</b>\nПоисков: {searches}\nСохранено: {favs}",
        
        "match_100":   "✅ Всё есть",
        "match_high":  "✅ Почти всё ({pct}%)",
        "match_mid":   "🟡 Кое-чего не хватает",
        "match_low":   "🔴 Мало совпадений",
        "strict_warn": "⚠️ Идеальных нет. Показываю лучшие:",
        "random_title":  "🎲 <b>Случайный рецепт:</b>",
    },
    "en": {
        "welcome": (
            "👋 <b>Hi! I'm Chef Bot.</b>\n"
            "I'll help you cook delicious meals with what you have.\n\n"
            "🍅 <b>Just type your ingredients</b>:\n"
            "<i>chicken, potato, onion, cheese</i>\n\n"
            "I'll find recipes, show you what's missing, and give you instructions!"
        ),
        "help": (
            "ℹ️ <b>How to use:</b>\n\n"
            "1. Type ingredients separated by commas.\n"
            "2. Swipe through recipes with the ⏭ button.\n"
            "3. Save favorites with ❤️.\n\n"
            "<b>Commands:</b>\n"
            "/fridge — my saved ingredients\n"
            "/mode — strict search (only my ingredients)\n"
            "/favorites — saved recipes\n"
            "/category — select meal type\n"
        ),
        "choose_category":    "🗂 Choose category:",
        "category_set":       "✅ Selected: <b>{cat}</b>\n\nNow type your ingredients:",
        "searching":          "🍳 Finding ideas for: <i>{ingredients}</i>...",
        "no_results":         "😕 Nothing found. Try different ingredients.",
        "results_header":     "👨‍🍳 <b>Found recipes!</b>",
        "too_short":          "❗ Type at least a couple of ingredients",
        "current_category":   "📂 Current category: <b>{cat}</b>",
        "error":              "⚠️ Network error. Please try again.",
        "btn_category":       "📂 Categories",
        "btn_next":           "⏭ Next recipe",
        "translating":        "⏳ Translating...",
        "no_more_recipes":    "No more recipes! Try different ingredients.",
        
        "lbl_from_your":      "Have",
        "lbl_buy_more":       "Need",
        "lbl_cooking":        "Recipe",
        "lbl_full_recipe":    "Read full",
        
        "mode_normal":        "🔍 Normal search",
        "mode_strict":        "🎯 Only my ingredients",
        "choose_mode":        "🔄 <b>Search Mode</b>\n\n🔍 Normal — more results.\n🎯 Strict — only what you have.",
        "mode_changed":       "✅ Mode changed: <b>{mode}</b>",
        
        "fridge_contents":    "🥦 <b>My Fridge:</b>\n{items}\n\nTap «What to cook»!",
        "fridge_empty":       "🥦 Fridge is empty. Type ingredients to save them!",
        "fridge_empty_cook":  "Type your ingredients first!",
        "fridge_cleared":     "🗑 Cleared!",
        "btn_clear_fridge":   "🗑 Clear",
        "btn_toggle_mode":    "🔄 Mode: {mode}",
        "btn_whatcook":       "👨‍🍳 What to cook?",
        
        "favorites_empty":    "⭐ No favorites yet.",
        "favorites_header":   "⭐ <b>Favorite recipes:</b>",
        "fav_added":          "❤️ Saved!",
        "fav_already":        "Already saved",
        "fav_removed":        "Removed",
        "fav_not_found":      "Not found",
        
        "stats_text":         "📊 <b>Stats:</b>\nSearches: {searches}\nSaved: {favs}",
        
        "match_100":   "✅ Have everything",
        "match_high":  "✅ Almost everything ({pct}%)",
        "match_mid":   "🟡 Missing some",
        "match_low":   "🔴 Missing a lot",
        "strict_warn": "⚠️ No perfect matches. Showing best:",
        "random_title":  "🎲 <b>Surprise recipe:</b>",
    },
}
