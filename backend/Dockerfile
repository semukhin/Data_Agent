FROM python:3.10-slim

WORKDIR /app

# Установка базовых зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Копирование файлов зависимостей и установка
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование кода приложения
COPY . .

# Создание пользователя без прав root
RUN addgroup --system app && adduser --system --group app
RUN chown -R app:app /app
USER app

# Определение переменной окружения для порта
ENV PORT=9000

# Запуск приложения
CMD uvicorn app.main:app --host 0.0.0.0 --port $PORT