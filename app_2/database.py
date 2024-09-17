from tortoise import Tortoise, fields
from tortoise.models import Model
from datetime import datetime
import os
from dotenv import load_dotenv
import asyncio
import asyncpg

# Загружаем переменные окружения из .env файла
load_dotenv()

POSTGRES_USER = os.getenv('POSTGRES_USER')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')
POSTGRES_DB = os.getenv('POSTGRES_DB')
POSTGRES_HOST = os.getenv('POSTGRES_HOST')


# Модель для хранения данных о товарах
class ProductCard(Model):
    id = fields.IntField(pk=True)
    marketplace = fields.CharField(max_length=50)  # Маркетплейс
    product_name = fields.CharField(max_length=255)  # Название товара
    product_url = fields.TextField()  # URL товара
    price = fields.DecimalField(max_digits=20, decimal_places=2)  # Текущая цена товара
    date = fields.DatetimeField(default=datetime.now)  # Дата получения данных


# Функция для ожидания подключения к базе данных
async def wait_for_db():
    while True:
        try:
            conn = await asyncpg.connect(
                user=POSTGRES_USER,
                password=POSTGRES_PASSWORD,
                database=POSTGRES_DB,
                host=POSTGRES_HOST
            )
            await conn.close()
            break
        except (asyncpg.exceptions.CannotConnectNowError, OSError):
            print("База данных ещё не готова. Ожидание...")
            await asyncio.sleep(5)  # Ждём 5 секунд перед повторной попыткой


# Функция для инициализации базы данных
async def init_db():
    await wait_for_db()  # Ожидание подключения к базе данных
    db_url = f'postgres://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:5432/{POSTGRES_DB}'
    await Tortoise.init(
        db_url=db_url,
        modules={'models': ['database']}
    )
    await Tortoise.generate_schemas()


# Функция для сохранения данных о товаре в базу данных
async def save_product_to_db(data):
    await ProductCard.create(
        marketplace=data['marketplace'],
        product_name=data['product_name'],
        product_url=data['product_url'],
        price=data['price'],
        date=data['date']
    )
