# Используем официальный образ Python
FROM python:3.10-slim

# Устанавливаем зависимости для PostgreSQL, Playwright и системные библиотеки
RUN apt-get update && apt-get install -y \
    libpq-dev gcc curl libglib2.0-0 libnss3 libnspr4 libdbus-1-3 libatk1.0-0 \
    libatk-bridge2.0-0 libcups2 libdrm2 libxkbcommon0 libatspi2.0-0 libxcomposite1 \
    libxdamage1 libxext6 libxfixes3 libxrandr2 libgbm1 libpango-1.0-0 libcairo2 libasound2 && \
    pip install --upgrade pip && \
    pip install --no-cache-dir playwright

# Устанавливаем только Chromium для Playwright с увеличенным таймаутом
RUN PLAYWRIGHT_BROWSERS_PATH=/ms-playwright-cache playwright install chromium

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файл requirements.txt из корневой директории в контейнер
COPY ./requirements.txt /app/

# Устанавливаем зависимости из requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Копируем все файлы приложения в контейнер
COPY . /app

# Команда для запуска приложения с указанием пути к браузерам
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright-cache
CMD ["python", "main.py"]

