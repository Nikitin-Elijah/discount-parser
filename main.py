import requests
from user_agent import generate_user_agent
from bs4 import BeautifulSoup
import lxml
import json
import re


def collect_data(shop_code):
    cookies = {
        'shopCode': shop_code,
    }
    headers = {
        'User-Agent': generate_user_agent(),
    }

    # Получаем первую страницу, чтобы определить количество страниц
    response = requests.get('https://magnit.ru/promo-catalog', cookies=cookies, headers=headers)
    max_of_pagination = int(
        BeautifulSoup(response.text, 'lxml').find('nav', class_='pl-pagination__pager').find_all('span',
                                                                                                 class_='pl-button__icon')[
            -1].text)

    # Сохраняем HTML ответ первой страницы
    with open('result.html', 'w', encoding="utf-8") as file:
        file.write(response.text)

    catalog = {}

    for page in range(1, max_of_pagination + 1):
        response = requests.get(
            f'https://magnit.ru/promo-catalog?utm_source=magnit.ru&utm_campaign=navbar&utm_medium=promo&page={page}',
            cookies=cookies, headers=headers)

        # Сохраняем HTML ответ текущей страницы
        with open('result.html', 'w', encoding="utf-8") as file:
            file.write(response.text)

        soap = BeautifulSoup(response.text, 'lxml')  # Используем response.text напрямую
        cards = soap.find_all('div',
                              class_='pl-stack-item pl-stack-item_size-6 pl-stack-item_size-4-m pl-stack-item_size-3-ml unit-catalog__stack-item')

        for card in cards:
            card_title = card.find('div', class_='pl-text unit-catalog-product-preview-title')
            card_prices = card.find('span', class_='pl-text unit-catalog-product-preview-prices__regular')

            if card_title and card_prices:
                product_type = re.search(r'\b[а-яёА-ЯЁ][а-яё]+\b', card_title.text)
                if product_type:
                    product_type = product_type.group(0)
                    if product_type not in catalog:
                        catalog[product_type] = []
                    catalog[product_type].append(
                        {'title': card_title.text, 'price': card_prices.text.replace('\u200a', ''), 'page': page})

        print(f'[+] pages passed {page}/{max_of_pagination}')

    # Сохраняем собранные данные в JSON
    with open('products.json', 'w', encoding='utf-8') as fh:
        json.dump(catalog, fh, ensure_ascii=False)


def main():
    shop_code = 'код магазина из cookie'
    collect_data(shop_code)


if __name__ == '__main__':
    main()