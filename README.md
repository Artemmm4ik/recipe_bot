# 👨‍🍳 Recipe Bot — Telegram бот для поиска рецептов

Бот находит рецепты по ингредиентам из твоего холодильника.
Поддерживает **8 категорий** (диета, спорт, десерт, веган и др.) и **два языка** (RU/EN — автоопределение).

---

## ✨ Возможности

| Функция | Описание |
|---|---|
| 🔍 Поиск по ингредиентам | Введи продукты через запятую |
| 🏷 8 категорий | Любой · Диета · Спорт · Десерт · Веган · Быстро · Суп · Кето |
| 🌍 2 языка | RU/EN — определяется автоматически |
| ⚡ Параллельный поиск | Сразу 4–5 сайтов одновременно |
| 🔗 Прямые ссылки | povarenok.ru, russianfood.com, edimdoma.ru, food.ru, allrecipes.com |

---

## 🚀 Деплой на render.com (шаг за шагом)

### Шаг 1 — Создай бота в Telegram

1. Открой [@BotFather](https://t.me/BotFather) в Telegram
2. Напиши `/newbot`
3. Придумай имя (например: `Мой шеф-повар`) и username (например: `mychef_recipe_bot`)
4. **Скопируй токен** — он выглядит как `1234567890:ABCdefGHI...`

### Шаг 2 — Загрузи проект на GitHub

```bash
git init
git add .
git commit -m "Initial recipe bot"
# Создай репозиторий на github.com и:
git remote add origin https://github.com/ТВО_ИМЯПОЛЬЗОВАТЕЛЯ/recipe-bot.git
git push -u origin main
```

### Шаг 3 — Задеплой на render.com

1. Зайди на [render.com](https://render.com) → **New +** → **Web Service**
2. Подключи свой GitHub репозиторий
3. Настройки подтянутся автоматически из `render.yaml`:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python main.py`
4. Перейди в **Environment** → добавь переменные:

| Переменная | Значение |
|---|---|
| `TELEGRAM_BOT_TOKEN` | Токен от @BotFather |
| `WEBHOOK_URL` | URL сервиса (см. ниже) |

> **Где взять WEBHOOK_URL?**
> После первого деплоя render.com покажет URL вида `https://recipe-bot-xxxx.onrender.com`.
> Скопируй его и добавь в переменную `WEBHOOK_URL` (без слеша в конце).
> Затем нажми **Manual Deploy** → бот запустится с webhook.

### Шаг 4 — Готово!

Открой своего бота в Telegram и напиши `/start` 🎉

---

## 🛠 Локальная разработка

```bash
# 1. Установи зависимости
cd recipe_bot
python3 -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 2. Создай .env
cp .env.example .env
# Открой .env, вставь TELEGRAM_BOT_TOKEN
# НЕ указывай WEBHOOK_URL → запустится в режиме polling

# 3. Самопроверка (не нужен токен и интернет)
python test_all.py

# 4. Запуск бота
python main.py
```

---

## 📂 Структура проекта

```
recipe_bot/
├── main.py              # Точка входа: webhook (render.com) / polling (локально)
├── config.py            # 8 категорий + тексты RU/EN
├── requirements.txt     # Зависимости Python
├── render.yaml          # Конфиг для render.com
├── Dockerfile           # Docker образ (опционально)
├── .env.example         # Шаблон переменных окружения
├── test_all.py          # 40 локальных тестов
├── test_parser.py       # Тест парсера (требует интернет)
├── handlers/
│   ├── start.py         # /start и /help
│   ├── category.py      # /category + inline-кнопки
│   └── recipe.py        # Парсинг и вывод рецептов
├── parsers/
│   └── recipe_parser.py # Параллельный парсинг 5 сайтов
└── utils/
    └── user_state.py    # Хранение языка и категории
```

---

## 💬 Как пользоваться

```
/start          — приветствие и инструкция
/category       — выбрать тип (диета / спорт / десерт и т.д.)
/help           — справка

курица, картошка, лук        ← просто напиши продукты
eggs, rice, garlic            ← работает и по-английски
```

---

## ⚠️ Особенности render.com free tier

- Сервис **засыпает** через 15 мин неактивности → **первое сообщение разбудит** его (~30 сек)
- Чтобы не засыпал — подключи [UptimeRobot](https://uptimerobot.com) для пинга `/health` каждые 10 мин (бесплатно)
- Webhook активируется автоматически при старте — настраивать вручную не нужно

---

## 🔧 Технологии

- **python-telegram-bot 20.7** — асинхронный Telegram SDK
- **aiohttp** — HTTP-сервер (webhook + health check) и параллельные запросы
- **BeautifulSoup4 + lxml** — парсинг HTML
- **langdetect** — автоопределение языка RU/EN
- **python-dotenv** — переменные окружения
