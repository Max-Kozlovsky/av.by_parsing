import requests
from bs4 import BeautifulSoup
import csv
import json
from typing import Union

# BMW e60 car search query link
search_url = 'https://cars.av.by/filter?brands[0][brand]=8&brands[0][model]=5865&brands[0][generation]=4441'

HEADERS = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,'
              'application/signed-exchange;v=b3;q=0.9',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
                  'Chrome/103.0.0.0Safari/537.36'
}


def get_number():
    """Generator function. Returns the next ordinal number of the found declaration."""
    num = 1
    while True:
        yield num
        num += 1


def search_ads(url: str) -> list:
    """
    The function accepts a link with a selection of ads from the site av.by and selects information from the site
    according to the given parameters. The information is stored as a list.
    :param url: str
    :return: list
    """
    info: Union[dict, list] = {}  # dictionary for storing information from ads
    number = get_number()  # creating a serial number

    request: str = requests.get(url, headers=HEADERS).text  # web page request
    soup = BeautifulSoup(request, 'html.parser')  # processing data from a request
    # count of pages in pagination
    count_pages: int = int(soup.find('h3', class_='listing__title').text.split()[1]) // 25 + 1

    for page in range(1, count_pages + 1):  # loop through pagination links
        target_url = url + f'&page={page}'  # create a link
        print(f'Считываю {page} страницу')
        target_request = requests.get(target_url, headers=HEADERS).text  # get data from link
        soup_cars = BeautifulSoup(target_request, 'html.parser')  # processing data
        cards = soup_cars.find_all('div', class_='listing-item__wrap')  # find ad
        for card in cards:  # parsing each ad
            name: str = card.find('span', class_='link-text').text  # ad title
            link: str = 'https://cars.av.by/' + card.find('a', class_='listing-item__link').get('href')  # ad link
            price_byn: str = card.find('div', class_='listing-item__price').text.replace('\xa0', '') \
                .replace('\u2009', '')  # price in roubles
            price_usd = int(''.join(card.find('div', class_='listing-item__priceusd').text
                                    .replace('$', '').split()[1:]))  # price in dollars
            params: str = card.find('div', class_='listing-item__params').text.replace('\xa0', '') \
                .replace('\u2009', '').split()  # other options
            year: str = params[0].split('.')[0]  # year of issue
            transmission: str = params[0].split('.')[1].replace(',', '')  # transmission type
            engine: str = params[1].replace(',', '')  # engine volume
            fuel: str = params[2].replace(',', '')  # fuel type
            body_type: str = ''  # body type
            for i in params[-1]:
                if i.isalpha():
                    body_type += i
                else:
                    break
            mileage: str = params[-1].replace(body_type, '')  # car mileage
            info.update(
                {next(number): [link,
                                name,
                                price_byn,
                                price_usd,
                                year,
                                transmission,
                                engine,
                                fuel,
                                body_type,
                                mileage]})  # add data to dictionary
    info: list = sorted(info.values(), key=lambda x: x[2])  # sort by price in dollars
    return info


def write_csv(url_data: list):
    """
    The function writes data from the search_ads function in csv format
    :param url_data : information about cars for sale
    :return: None
    """
    with open('BMW.csv', 'w', newline='') as file:
        car_writer = csv.writer(file, delimiter=';')
        car_writer.writerow(['Ссылка', 'Название', 'Цена BYN', 'Цена USD', 'Год выпуска', 'тип коробки', 'объем',
                             'вид топлива', 'тип кузова', 'пробег'])
        for value in url_data:
            car_writer.writerow([value[0], value[1], value[2], value[3], value[4], value[5], value[6], value[7],
                                 value[8], value[9]])
    print('BMW.csv file successfully written')


def write_json(url_data):
    """
        The function writes data from the search_ads function in json format
        :param url_data : information about cars for sale
        :return: None
        """
    with open('BMW.json', 'w', encoding='UTF-8') as file:
        json.dump(url_data, file, indent=4)
    print('BMW.json file successfully written')


data = search_ads(search_url)
write_csv(data)
write_json(data)
