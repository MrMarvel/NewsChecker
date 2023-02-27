import logging
import re
from typing import List, Dict

import requests
from bs4 import BeautifulSoup, ResultSet, Tag

from . import date_formats


def extract_documents_from_page(soup: BeautifulSoup) -> List[Dict]:
    # Извлечём все документы из страницы
    documents_html_list: ResultSet[Tag] = soup.findAll('div', {'class': 'doc_itm'})
    documents: List[Dict] = []

    # Получаем содержание каждого документа из списка
    for document_html in documents_html_list:
        try:
            doc_date_label_str = document_html.find('span', {'class': 'doc_itm__date'}).text.strip()
            date_label = re.search(r'\d{2}\.\d{2}\.\d{4}', doc_date_label_str)
            if date_label is None:
                logging.warning(f'Не удалось извлечь дату из строки: {doc_date_label_str}')
                continue
            doc_date_str = date_label.group(0)
            doc_date = date_formats.get_date_from_str_digital(doc_date_str)
            doc_title_str = document_html.find('p', {'class': 'doc_itm__title'}).text.strip()

            span_shown = document_html.find('span', {'class': None})
            doc_description_str = span_shown.text.strip() if span_shown is not None else ''
            span_hiden = document_html.find('span', {'class': 'js-more-hide'})
            doc_description_str += span_hiden.text.strip() if span_hiden is not None else ''

            doc_link_str = document_html.find('a').attrs.get('href', None)

            document_tuple = {'date': doc_date,
                              'title': doc_title_str,
                              'description': doc_description_str}

            if doc_link_str is not None:
                document_tuple['link'] = doc_link_str

            documents.append(document_tuple)
        except Exception as e:
            logging.exception(f"Ошибка при обработке документа: {e}. Пропускаем документ с содержимым: {document_html}")
    return documents


def get_information_news_from_site(year: int, page_num: int = 1):
    if page_num < 1:
        exp_message = f"Попытка получить страницу с неправильным номером \"{page_num}\"!"
        logging.exception(exp_message)
        raise Exception(exp_message)

    url = f'https://nfreg.ru/documents-category/{year}/page/{page_num}'
    response = requests.get(url)
    if response.status_code != 200:
        exp_message = f"Ошибка получения страницы \"{page_num}\" из \"{year}\" года! " \
                      f"Запрос: {response}"
        logging.exception(exp_message)
        raise Exception(exp_message)

    # Parse the HTML content using BeautifulSoup

    soup = BeautifulSoup(response.content, 'html.parser')

    documents = extract_documents_from_page(soup)

    return documents
