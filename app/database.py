import csv
import os
from tortoise import Tortoise, fields
from tortoise.models import Model
import asyncio
import asyncpg
from dotenv import load_dotenv
from datetime import datetime
import pytz  # Импортируем pytz для работы с часовыми поясами

# Загружаем переменные из .env файла
load_dotenv()

# Получаем переменные среды
POSTGRES_USER = os.getenv('POSTGRES_USER')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')
POSTGRES_DB = os.getenv('POSTGRES_DB')
POSTGRES_HOST = os.getenv('POSTGRES_HOST')


# Модель для хранения данных о ценах с бирж
class PriceRecord(Model):
    id = fields.IntField(pk=True)
    exchange = fields.CharField(max_length=50)  # Название биржи
    pair = fields.CharField(max_length=50)  # Валютная пара
    price = fields.DecimalField(max_digits=20, decimal_places=8)  # Текущая цена
    previous_price = fields.DecimalField(max_digits=20, decimal_places=8,
                                         null=True)  # Предыдущая цена
    max_price = fields.DecimalField(max_digits=20, decimal_places=8,
                                    null=True)  # Максимальная цена (если есть)
    min_price = fields.DecimalField(max_digits=20, decimal_places=8,
                                    null=True)  # Минимальная цена (если есть)
    date = fields.DatetimeField(auto_now_add=False, use_tz=True,
                                null=True)  # Дата и время записи с использованием временной зоны
    difference = fields.DecimalField(max_digits=5, decimal_places=3,
                                     null=True)  # Разница в процентах
    total_amount = fields.DecimalField(max_digits=10, decimal_places=2,
                                       null=True)  # Объем сделок (если есть)
    holdings_value = fields.DecimalField(max_digits=20, decimal_places=8,
                                         null=True)  # Стоимость накопленных BTC


# Функция для сохранения данных в CSV
def save_to_csv(data):
    with open('prices.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([
            data['exchange'],
            data['pair'],
            data['price'],
            data.get('max price', None),
            data.get('min price', None),
            data.get('date', None),
            data.get('difference', None),
            data.get('total amount', None),
            data.get('holdings_value', None)
        ])


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


# Функция для извлечения предыдущей цены из базы данных для конкретной биржи и валютной пары
async def get_previous_price(exchange, pair):
    # Извлекаем последнюю запись для конкретной биржи и валютной пары
    previous_record = await PriceRecord.filter(exchange=exchange, pair=pair).order_by('-id').first()
    if previous_record:
        return float(previous_record.price)  # Возвращаем предыдущую цену
    return None  # Если записи нет, возвращаем None


# Функция для сохранения данных в базу данных и CSV
async def save_to_db(exchange, pair, data, previous_price=None):
    # Текущая цена
    current_price = float(data['price'])

    # Количество BTC, накопленных Лакрицей
    BTC_HOLDINGS = 3

    # Вычисляем разницу
    if previous_price is not None:
        difference = (current_price - previous_price) / previous_price * 100  # Разница в процентах
    else:
        difference = None  # Если предыдущей цены нет, разницу вычислить невозможно

    # Рассчитываем стоимость накопленных BTC
    holdings_value = BTC_HOLDINGS * current_price

    # Получаем текущее московское время
    moscow_tz = pytz.timezone('Europe/Moscow')
    current_datetime = data.get('date', datetime.now(moscow_tz))  # Используем московское время

    # Сохраняем запись в базу данных
    await PriceRecord.create(
        exchange=exchange,  # Название биржи
        pair=pair,  # Валютная пара
        price=current_price,
        previous_price=previous_price,
        max_price=data.get('max price', None),  # Максимальная цена (если есть)
        min_price=data.get('min price', None),  # Минимальная цена (если есть)
        date=current_datetime,  # Используем московское время
        difference=difference,  # Разница в цене
        total_amount=data.get('total amount', None),  # Объем сделок (если есть)
        holdings_value=holdings_value  # Стоимость накопленных BTC
    )

    # Подготовка данных для сохранения в CSV
    csv_data = {
        'exchange': exchange,
        'pair': pair,
        'price': current_price,
        'max price': data.get('max price', None),
        'min price': data.get('min price', None),
        'date': current_datetime,
        'difference': difference,
        'total amount': data.get('total amount', None),
        'holdings_value': holdings_value
    }

    # Сохраняем данные в CSV
    save_to_csv(csv_data)
