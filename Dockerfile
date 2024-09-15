# Используем официальный образ Python
FROM python:3.10-slim

# Устанавливаем зависимости для PostgreSQL
RUN apt-get update && apt-get install -y \
    libpq-dev gcc && \
    rm -rf /var/lib/apt/lists/*

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем все файлы проекта в контейнер
COPY . /app

# Устанавливаем зависимости из requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Команда для запуска приложения
CMD ["python", "app/main.py"]
