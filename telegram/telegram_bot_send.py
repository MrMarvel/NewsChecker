import logging
import time

import requests


def get_telegram_id(username: str, bot_token: str) -> int | None:
    telegram_url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
    payload = {
        "offset": 0,
        "limit": 100,
        "allowed_updates": ["message"]
    }

    response = requests.post(telegram_url, data=payload)
    if response.status_code == 200:
        chat_data = response.json()
        for message in chat_data["result"]:
            if "chat" in message["message"] and \
                    "username" in message["message"]["chat"] and \
                    message["message"]["chat"]["username"] == username:
                return message["message"]["chat"]["id"]
        print("Error: User not found")
        return None
    else:
        print(f"Error getting chat data: {response.text}")
        return None


last_send_time = None
min_period_between_sends = 1  # seconds


def send_telegram_to_user(username: str, msg: str, bot_token: str):
    global last_send_time
    now = time.time()
    if last_send_time is not None and now - last_send_time < min_period_between_sends:
        logging.info("Too fast sending messages. Waiting...")
        time.sleep(min_period_between_sends - (now - last_send_time))
    last_send_time = time.time()


    user_id = get_telegram_id(username, bot_token)
    if user_id is None:
        raise Exception("Не могу отправить сообщение в Telegram потому что user id не был определён!\n"
                        "Пожалусйста проверьте \"username\" в конфигурации!")

    telegram_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": user_id,
        "text": msg
    }

    response = requests.post(telegram_url, data=payload)
    if response.status_code == 200:
        logging.info("Message sent successfully!")
    else:
        logging.error(f"Error sending message: {response.text}. Ошибка: {response.content}")
        raise Exception(f"Error sending message: {response.text}. Ошибка: {response.content}")
