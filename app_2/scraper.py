import time
from datetime import datetime
from database import save_product_to_db
from csv_writer import save_to_csv
from playwright.async_api import async_playwright, TimeoutError


# Функция для проверки антибота и обновления страницы на Ozon
async def handle_antibot(page):
    try:
        # Проверим, есть ли признаки антибота
        antibot_element = await page.query_selector('text="Доступ ограничен"')
        if antibot_element:
            print("Антибот обнаружен, обновляем страницу...")
            await page.reload(wait_until="domcontentloaded")
            return True  # Обновили страницу
        return False  # Антибота нет
    except Exception as e:
        print(f"Ошибка при проверке антибота: {e}")
        return False


# Функция для парсинга маркетплейса
async def scrape_marketplace(page, marketplace, url, search_query):
    try:
        # Переход на страницу
        await page.goto(url, wait_until="domcontentloaded", timeout=60000)
        time.sleep(10)

        # Проверка и обработка антибота для Ozon
        if marketplace == "Ozon":
            while await handle_antibot(page):
                print(f"Перезагрузка страницы на {marketplace} из-за антибота...")
                time.sleep(5)

        # Убедимся, что поле поиска существует
        if marketplace == "Wildberries":
            search_input = await page.query_selector('input[placeholder="Найти на Wildberries"]')
        elif marketplace == "Ozon":
            search_input = await page.query_selector(
                'input[placeholder="Искать на Ozon"], input[placeholder="Найти товары"]')

        if search_input:
            # Заполняем поле поиска
            await search_input.fill(search_query)
            time.sleep(5)
            await handle_antibot(page)  # Проверка антибота после заполнения
            # Нажимаем клавишу Enter для поиска
            await search_input.press('Enter')
            time.sleep(5)
            await handle_antibot(page)  # Проверка антибота после нажатия Enter
        else:
            print(f"Поле поиска не найдено на {marketplace}")
            return

        # Ожидание загрузки результатов поиска
        await page.wait_for_selector('.product-card' if marketplace == "Wildberries" else '.j3o_23',
                                     timeout=60000)
        time.sleep(5)
        await handle_antibot(page)  # Проверка антибота после загрузки результатов
        time.sleep(4)

        # Открываем фильтр сортировки
        if marketplace == "Wildberries":
            await page.click('.dropdown-filter__btn')
            time.sleep(2)
            await handle_antibot(page)  # Проверка антибота после нажатия фильтра
            time.sleep(2)
            await page.wait_for_selector('.dropdown-filter__content', timeout=30000)
            time.sleep(2)
            await handle_antibot(page)  # Проверка антибота после загрузки фильтра
            time.sleep(2)
            await page.click('text="По возрастанию цены"')
            time.sleep(2)
            await handle_antibot(page)  # Проверка антибота после выбора сортировки
            time.sleep(2)
        elif marketplace == "Ozon":
            await page.click('input[title="Популярные"]')
            time.sleep(5)
            await handle_antibot(page)  # Проверка антибота после открытия сортировки
            time.sleep(5)
            await page.click('text="Дешевле"')
            time.sleep(5)
            await handle_antibot(page)  # Проверка антибота после выбора сортировки
            time.sleep(5)

        # Ожидаем обновления товаров после выбора сортировки
        time.sleep(5)
        await page.wait_for_selector('.product-card' if marketplace == "Wildberries" else '.j3o_23',
                                     timeout=60000)
        time.sleep(5)
        await handle_antibot(page)  # Проверка антибота после обновления товаров

        # Извлекаем первую карточку товара (самый дешевый товар)
        first_product = await page.query_selector(
            '.product-card' if marketplace == "Wildberries" else '.j3o_23')

        if first_product:
            # Извлекаем название товара
            if marketplace == "Wildberries":
                product_name_element = await first_product.query_selector('.product-card__name')
            else:  # Ozon
                product_name_element = await first_product.query_selector('.tsBody500Medium')
            product_name = await product_name_element.text_content() if product_name_element else "Unknown Product"

            # Извлекаем цену товара
            if marketplace == "Wildberries":
                product_price_element = await first_product.query_selector('.price__lower-price')
            else:  # Ozon
                product_price_element = await first_product.query_selector('.c3015-a1')
            product_price_raw = await product_price_element.text_content() if product_price_element else "0"
            product_price = float(product_price_raw.replace('\u00A0', '').replace('₽', '').strip())

            # Извлекаем ссылку на товар
            if marketplace == "Wildberries":
                product_url_element = await first_product.query_selector('.product-card__link')
            else:  # Ozon
                product_url_element = await first_product.query_selector('a.tile-hover-target')
            product_url = await product_url_element.get_attribute(
                'href') if product_url_element else url

            # Формируем данные для сохранения
            product_data = {
                'marketplace': marketplace,
                'product_name': product_name.strip(),
                'product_url': (
                    f"https://www.wildberries.ru{product_url}"
                    if product_url and not product_url.startswith(
                        'http') and marketplace == "Wildberries"
                    else f"https://www.ozon.ru{product_url}" if product_url and not product_url.startswith(
                        'http') and marketplace == "Ozon"
                    else product_url
                ),
                'price': product_price,
                'date': datetime.now()
            }

            # Сохраняем данные в БД и CSV
            await save_product_to_db(product_data)
            save_to_csv(product_data)

            print(f"Товар сохранен: {product_data}")
        else:
            print(f"Товар не найден на {marketplace}.")
    except TimeoutError:
        print(f"Timeout error on {marketplace}, restarting...")
        raise  # Перезапуск будет инициирован в функции scrape_all_marketplaces


# Функция для парсинга всех маркетплейсов
async def scrape_all_marketplaces():
    while True:
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(
                    headless=False)  # не забываем менять на True, если работаем в докере
                page = await browser.new_page()

                # Общий список маркетплейсов
                marketplaces = [
                    {'name': 'Wildberries', 'url': 'https://www.wildberries.ru/'},
                    {'name': 'Ozon', 'url': 'https://www.ozon.ru/'},
                    # {'name': 'Yandex Market', 'url': 'https://market.yandex.ru/'}
                ]

                # Список товаров для поиска
                search_queries = ['копье', 'дуршлаг', 'красные носки', 'леска для спиннинга']

                # Парсим каждый товар на всех маркетплейсах
                for query in search_queries:
                    for mp in marketplaces:
                        print(f"Парсим {query} на {mp['name']}")
                        await handle_antibot(page)
                        time.sleep(2)
                        await scrape_marketplace(page, mp['name'], mp['url'], query)
                        time.sleep(10)
                        await handle_antibot(page)  # Проверка антибота после открытия сортировки
                        time.sleep(5)  # Добавляем небольшую паузу между запросами

                await browser.close()

            # Выход из цикла, если завершение успешно
            break
        except Exception as e:
            print(f"Ошибка: {e}, перезапуск через 5 секунд...")
            time.sleep(5)  # Ожидание перед перезапуском
