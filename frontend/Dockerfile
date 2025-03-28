FROM node:21-alpine

WORKDIR /app

# Копирование файлов зависимостей
COPY package.json package-lock.json ./

# Установка зависимостей
RUN npm ci

# Копирование исходного кода
COPY . .

# Сборка приложения
RUN npm run build

# Установка сервера для раздачи статических файлов
RUN npm install -g serve

# Определение переменной окружения для порта
ENV PORT=3000

# Запуск приложения
CMD ["serve", "-s", "build", "-l", "3000"]