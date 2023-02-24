import logging
import os
from datetime import datetime, date
from typing import List, Dict

from config.config_utils import create_or_update_config
from grabber.news_grabber import get_latest_news
from telegram.telegram_bot_send import send_telegram_to_user


def remove_checked_news_from_list(news_list: List[Dict], last_check: datetime):
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
            inform(n1, n2, today_check)
        except Exception as e:
            logging.error(f"Не получилось отправить уведомление вообще. Исключение: {e}\n"
                          f"Выход из приложения")
            return
    else:
        logging.info(f"Новостей нет!")
    with open('last_check.txt', mode='w') as f:
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
    date = e.get('date', datetime.today())
    link = e.get('link', None)
    if event_num != 0:
        msg += "\n"
    msg += f"{event_num + 1}. {e.get('title')}\n"
    if type(date) is date:
        msg += f"{date.strftime('%d.%m.%Y')}\n"
    else:
        msg += f"{date.strftime('%d.%m.%Y %H:%M:%S')}\n"
    msg += f"{e.get('description')}...\n"
    if link is not None:
        msg += f"{link}\n"
    return msg


def inform(n1: List[Dict], n2: List[Dict], check_time: datetime):
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
    if os.path.exists('latest_log.txt'):
        # edit_timestamp = os.path.getmtime('latest_log.txt')
        # edit_date = datetime.fromtimestamp(edit_timestamp)
        for i in range(8, 1, -1):
            if os.path.exists(f'log{i}.txt'):
                os.replace(f"log{i}.txt", f"log{i + 1}.txt")
        os.replace("latest_log.txt", "log2.txt")
        # os.rename('latest_log.txt', edit_date.strftime("log1.txt"))
    logging.basicConfig(filename='latest_log.txt', filemode='w', encoding='utf-8', level=logging.DEBUG)
    get_unchecked_news_and_inform()
    cfg = create_or_update_config()
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
