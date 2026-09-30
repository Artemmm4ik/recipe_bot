FROM python:3.11-slim

WORKDIR /app

# Зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем проект
COPY . .

# Render.com сам задаёт PORT
ENV PORT=10000

CMD ["python", "main.py"]
