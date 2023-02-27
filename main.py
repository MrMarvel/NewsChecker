import logging
import os
from copy import deepcopy
from datetime import datetime, date
from typing import List, Dict

from config.config_utils import create_or_update_config
from grabber.news_grabber import get_latest_news
from grabber import documents_grabber
from telegram.telegram_bot_send import send_telegram_to_user


def compare_date_or_datetime(d1, d2, cmp='<='):
    if type(d1) is date and type(d2) is not date:
        d2 = d2.date()

    if type(d1) is not date and type(d2) is date:
        d1 = d1.date()

    if cmp == '<=':
        return d1 <= d2
    elif cmp == '>=':
        return d1 >= d2
    elif cmp == '<':
        return d1 < d2
    elif cmp == '>':
        return d1 > d2
    elif cmp == '==':
        return d1 == d2
    elif cmp == '!=':
        return d1 != d2


def remove_checked_news_from_list(news_list: List[Dict], last_check: datetime) -> None:
    for event in news_list.copy():
        e_date = event.get('date', datetime.fromtimestamp(0))
        last_check_date = last_check
        if type(e_date) is date:
            last_check_date = last_check_date.date()
        if e_date <= last_check_date:
            news_list.remove(event)


def get_unchecked_news_and_inform():
    last_check = None
    today_check = datetime.today()
    if os.path.exists('last_check.txt'):
        try:
            with open('last_check.txt', mode='r') as f:
                last_check_str = f.read()
                last_check = datetime.strptime(last_check_str, "%d.%m.%Y %H:%M:%S")
        except Exception as e:
            logging.exception(e)

    if last_check is None:
        last_check = datetime.fromtimestamp(0)

    n1, n2 = get_latest_news()

    remove_checked_news_from_list(n1, last_check)
    remove_checked_news_from_list(n2, last_check)

    if len(n1) > 0 or len(n2) > 0:
        logging.info(f"Новые новости [{n1},{n2}]")
        try:
            inform_news(n1, n2, today_check)
        except Exception as e:
            logging.error(f"Не получилось отправить уведомление вообще. Исключение: {e}\n")
            return
    else:
        logging.info(f"Новостей нет!")
    with open('last_check.txt', mode='w') as f:
        f.write(today_check.strftime("%d.%m.%Y %H:%M:%S"))


def remove_checked_documents(docs: List[Dict], last_check) -> List[Dict]:
    cleared_docs = deepcopy(docs)
    remove_checked_news_from_list(cleared_docs, last_check=last_check)
    return cleared_docs


def get_unchecked_documents_and_inform():
    last_check = None
    today_check = datetime.today()
    if os.path.exists('last_check_documents.txt'):
        try:
            with open('last_check_documents.txt', mode='r') as f:
                last_check_str = f.read()
                last_check = datetime.strptime(last_check_str, "%d.%m.%Y %H:%M:%S")
        except Exception as e:
            logging.exception(e)

    if last_check is None:
        last_check = datetime.fromtimestamp(0)

    unchecked_documents: List[Dict] = []

    page_num = 1
    max_pages_check = cfg.getint('documents', 'max_pages_per_check', fallback=2)
    while True:
        if page_num > max_pages_check:
            break
        try:
            documents_from_page = documents_grabber.get_information_news_from_site(today_check.year, page_num)
        except Exception as e:
            logging.exception(e)
            break
        if len(documents_from_page) == 0:
            break

        unchecked_documents_from_page = remove_checked_documents(documents_from_page, last_check)
        unchecked_documents.extend(unchecked_documents_from_page)

        # Если последний документ старше последней проверки, то дальше не идём
        if compare_date_or_datetime(documents_from_page[-1].get('date', datetime.fromtimestamp(0)),
                                    last_check, cmp='<='):
            break

        page_num += 1

    if len(unchecked_documents) > 0:
        logging.info(f"Новые документы {unchecked_documents}")
        try:
            inform_documents(unchecked_documents, today_check)
        except Exception as e:
            logging.error(f"Не получилось отправить уведомление вообще. Исключение: {e}")
            return
    else:
        logging.info(f"Документов нет!")
    with open('last_check_documents.txt', mode='w') as f:
        f.write(today_check.strftime("%d.%m.%Y %H:%M:%S"))


def inform_telegram(msg: str):
    cfg = create_or_update_config()
    try:
        send_telegram_to_user(cfg.get('telegram', 'username'), msg, cfg.get('telegram', 'bot_token', raw=True))
    except Exception as e:
        logging.exception(f"Send telegram exception: {e}")
        raise e


def make_telegram_event_text(e: Dict, event_num: int) -> str:
    msg = ""
    e_date = e.get('date', datetime.today())
    link = e.get('link', None)
    if event_num != 0:
        msg += "\n"
    msg += f"{event_num + 1}. {e.get('title')}\n"
    if type(e_date) is date:
        msg += f"{e_date.strftime('%d.%m.%Y')}\n"
    else:
        msg += f"{e_date.strftime('%d.%m.%Y %H:%M:%S')}\n"
    msg += f"{e.get('description')}...\n"
    if link is not None:
        msg += f"{link}\n"
    return msg


def make_telegram_document_text(e: Dict, event_num: int) -> str:
    msg = ""
    e_date = e.get('date', datetime.today())
    link = e.get('link', None)
    if event_num != 0:
        msg += "\n"
    msg += f"{event_num + 1}. {e.get('title')}\n"
    if type(e_date) is date:
        msg += f"{e_date.strftime('%d.%m.%Y')}\n"
    else:
        msg += f"{e_date.strftime('%d.%m.%Y %H:%M:%S')}\n"
    msg += f"{e.get('description')}\n"
    if link is not None:
        msg += f"{link}\n"
    return msg


def inform_documents(documents: List[Dict], check_time: datetime):
    cfg = create_or_update_config()
    failed_counter = 0
    failed_counter_max = 1
    if cfg.get('general', 'enable_telegram', fallback='false').lower() == 'true':
        msg_sections = [f"Документы сегодня {check_time.strftime('%d.%m.%Y %H:%M:%S')}.\n"]
        if len(documents) > 0:
            msg_sections[0] += f"Документы ({len(documents)} шт.):\n"
            for i, doc in enumerate(documents):
                msg_section = make_telegram_document_text(doc, i)
                if len(msg_sections[-1]) + len(msg_section) > 4096:
                    msg_sections.append(msg_section)
                else:
                    msg_sections[-1] += msg_section
        try:
            for msg in msg_sections:
                for i in range(0, len(msg), 4096):
                    inform_telegram(msg[i:i + 4096])
        except Exception as e:
            logging.exception(f"Не получилось отправить уведомление. Исключение: {e}")
            failed_counter += 1

    if failed_counter >= failed_counter_max:
        raise Exception("Не получилось отправить уведомление вообще")


def inform_news(n1: List[Dict], n2: List[Dict], check_time: datetime):
    cfg = create_or_update_config()
    failed_counter = 0
    failed_counter_max = 1
    if cfg.get('general', 'enable_telegram', fallback='false').lower() == 'true':
        msg = f"Новости сегодня {check_time.strftime('%d.%m.%Y %H:%M:%S')}.\n"
        if len(n1) > 0:
            msg += f"Новости Наро-Фоминского городского округа ({len(n1)} шт.):\n"
            for i, e in enumerate(n1):
                msg += make_telegram_event_text(e, i)
        if len(n2) > 0:
            msg += f"\nНовости Московской области ({len(n2)} шт.):\n"
            for i, e in enumerate(n2):
                msg += make_telegram_event_text(e, i)
        try:
            inform_telegram(msg)
        except Exception as e:
            failed_counter += 1
            logging.warning("Способ рассылки Telegram оказался неудачным.")
    if failed_counter == failed_counter_max:
        raise Exception("Полная неудача отправки")


if __name__ == '__main__':
    cfg = create_or_update_config()
    if os.path.exists('latest_log.txt'):
        # edit_timestamp = os.path.getmtime('latest_log.txt')
        # edit_date = datetime.fromtimestamp(edit_timestamp)
        for i in range(8, 1, -1):
            if os.path.exists(f'log{i}.txt'):
                os.replace(f"log{i}.txt", f"log{i + 1}.txt")
        os.replace("latest_log.txt", "log2.txt")
        # os.rename('latest_log.txt', edit_date.strftime("log1.txt"))
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    logging.basicConfig(filename='latest_log.txt', filemode='w', encoding='utf-8', level=logging.NOTSET)
    logging.debug("Начало работы программы")

    if cfg.get('general', 'check_news', fallback='false').lower() == 'true':
        logging.info("Ищем новые новости...")
        try:
            get_unchecked_news_and_inform()
        except Exception as e:
            logging.exception("Exception: ", e)
    if cfg.get('general', 'check_documents', fallback='false').lower() == 'true':
        logging.info("Ищем новые документы...")
        try:
            get_unchecked_documents_and_inform()
        except Exception as e:
            logging.exception("Exception: ", e)

    # if cfg.get('general', 'enable_email', fallback='false').lower() == 'true':
    #     try:
    #         send()
    #     except Exception as e:
    #         logging.exception("Send mail exception: ", e)
    #
    # if cfg.get('general', 'enable_telegram', fallback='false').lower() == 'true':
    #     try:
    #         send_telegram_to_user(cfg.get('telegram', 'username'), "HI", cfg.get('telegram', 'bot_token', raw=True))
    #     except Exception as e:
    #         logging.exception("Send telegram exception: ", e)
    # Call the function and print the results
