from datetime import date
from typing import Dict, List

import requests
from bs4 import BeautifulSoup, Tag, ResultSet

MONTHS = [
    'ЯНВАРЯ',
    'ФЕВРАЛЯ',
    'МАРТА',
    'АПРЕЛЯ',
    'МАЯ',
    'ИЮНЯ',
    'ИЮЛЯ',
    'АВГУСТА',
    'СЕНТЯБРЯ',
    'ОКТЯБРЯ',
    'НОЯБРЯ',
    'ДЕКАБРЯ',
]


def get_date_from_str(date_str: str) -> date:
    day_str, month_str, year_str = date_str.split(' ')
    day = int(day_str)
    month = MONTHS.index(month_str.upper()) + 1
    if month < 1:
        raise Exception(f"Не найден месяц: \"{date_str}\"")
    year = int(year_str)
    if year < 100:
        today = date.today()
        year += today.year // 100 * 100
    return date(year, month, day)


def extract_news_from_topic1(soup: BeautifulSoup):
    # Extract the news from the first topic
    all_news_from_topic1: ResultSet[Tag] = soup.findAll('a', {'class': 'news_itm js_slider_nav_itm'})
    all_news_formated_from_topic_1: List[Dict] = []

    # Получаем содержание объявления
    for event in all_news_from_topic1:
        event_date_str = event.find('p', {'class': 'news_itm__date'}).text.strip()
        event_date = get_date_from_str(event_date_str)
        event_title_str = event.find('p', {'class': 'news_itm__title'}).text.strip()
        event_description_str = event.find('div', {'class': 'news_itm__dsc'}).text.strip()
        event_link_str = event.attrs.get('href', None)
        event_tuple = {'date': event_date,
                       'title': event_title_str,
                       'description': event_description_str}
        event_image_div = event.find('div', {'class': 'news_itm__img'})
        if event_image_div is not None:
            inner_str_splitted = event_image_div.attrs.get('style', '').split('\'')
            if len(inner_str_splitted) > 1:
                if inner_str_splitted[1].startswith('http'):
                    event_image_url = inner_str_splitted[1]
                    event_tuple['image_url'] = event_image_url
        if event_link_str is not None:
            if event_link_str.startswith('http'):
                event_tuple['link'] = event_link_str

        all_news_formated_from_topic_1.append(event_tuple)
    return all_news_formated_from_topic_1


def extract_news_from_topic2(soup: BeautifulSoup):
    # Extract the news from the first topic
    all_news_from_topic1: ResultSet[Tag] = soup.findAll('div', {'class': 'news_itm_horizon'})
    all_news_formated_from_topic_1: List[Dict] = []

    # Получаем содержание объявления
    for event in all_news_from_topic1:
        event_date_str = event.find('p', {'class': 'news_itm_horizon__date'}).text.strip()
        event_date = get_date_from_str(event_date_str)
        event_title_str = event.find('p', {'class': 'news_itm_horizon__title'}).text.strip()
        event_description_str = event.find('div', {'class': 'news_itm_horizon__dsc'}).text.strip()
        title_element = event.find('p', {'class': 'news_itm_horizon__title'})
        event_tuple = {'date': event_date,
                       'title': event_title_str,
                       'description': event_description_str}
        event_image_div = event.find('div', {'class': 'news_itm_horizon__img'})
        if event_image_div is not None:
            event_image = event_image_div.find('img')
            if event_image is not None:
                if event_image.attrs.get('src', '').startswith('http'):
                    event_image_url = event_image.attrs.get('src', '')
                    event_tuple['image_url'] = event_image_url
        if title_element is not None:
            link_element = title_element.find('a')
            if link_element is not None:
                link = link_element.attrs.get('href', None)
                if link is not None:
                    if link.startswith('http'):
                        event_tuple['link'] = link

        all_news_formated_from_topic_1.append(event_tuple)
    return all_news_formated_from_topic_1


def get_latest_news():
    # Make a request to the website
    url = 'https://nfreg.ru/sobytiya/'
    response = requests.get(url)

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')

    news_topic_1 = extract_news_from_topic1(soup)

    news_topic_2 = extract_news_from_topic2(soup)

    # Return a tuple with the news for both topics
    return news_topic_1, news_topic_2
