import configparser
import logging
import os
import sys
from dataclasses import dataclass


@dataclass
class ConfigConstants:
    CONFIG_FILENAME = 'config.ini'
    EMAIL_TOPIC = 'email'
    FROM_EMAIL = 'from_email'
    TO_EMAIL = 'to_email'
    PASSWORD = 'password'
    EMAIL_DEFAULT = 'your_email@example.com'
    EMAIL_DEFAULT2 = 'recipient_email@example.com'


def create_or_update_config():
    """Creates or updates the config file with default settings."""
    config = configparser.ConfigParser()
    config_path = ConfigConstants.CONFIG_FILENAME

    logging.info(f"Проверяем файл конфигурации \"{ConfigConstants.CONFIG_FILENAME}\".")
    # If config file exists, read it and update missing or updated settings
    if os.path.exists(config_path):
        config.read(config_path)

        # Check if 'general' section exists, create it if not
        if not config.has_section('general'):
            config.add_section('general')

        # Check if 'enable_email' setting exists, create it if not
        if not config.has_option('general', 'enable_email'):
            config.set('general', 'enable_email', 'true')

        # Check if 'enable_telegram' setting exists, create it if not
        if not config.has_option('general', 'enable_telegram'):
            config.set('general', 'enable_telegram', 'true')

        # Check if 'email' section exists, create it if not
        if not config.has_section(ConfigConstants.EMAIL_TOPIC):
            config.add_section(ConfigConstants.EMAIL_TOPIC)

        # Check if 'from_email' setting exists, create it if not
        if not config.has_option(ConfigConstants.EMAIL_TOPIC, ConfigConstants.FROM_EMAIL):
            config.set(ConfigConstants.EMAIL_TOPIC, ConfigConstants.FROM_EMAIL, ConfigConstants.EMAIL_DEFAULT)

        # Check if 'to_email' setting exists, create it if not
        if not config.has_option(ConfigConstants.EMAIL_TOPIC, ConfigConstants.TO_EMAIL):
            config.set(ConfigConstants.EMAIL_TOPIC, ConfigConstants.TO_EMAIL, ConfigConstants.EMAIL_DEFAULT2)

        # Check if 'password' setting exists, create it if not
        if not config.has_option('email', 'password'):
            config.set('email', 'password', 'your_password')

        # Check if 'telegram' section exists, create it if not
        if not config.has_section('telegram'):
            config.add_section('telegram')

        # Check if 'bot_token' setting exists, create it if not
        if not config.has_option('telegram', 'bot_token'):
            config.set('telegram', 'bot_token', 'INSERT_YOUR_BOT_TOKEN')

        # Check if 'username' setting exists, create it if not
        if not config.has_option('telegram', 'username'):
            config.set('telegram', 'username', 'ExampleUser')

    # If config file does not exist, create it with default settings
    else:
        logging.info(f"Не было найдено \"{ConfigConstants.CONFIG_FILENAME}\". Создаём новый.")
        config['general'] = {
            'enable_email': 'true',
            'enable_telegram': 'true'
        }
        config[ConfigConstants.EMAIL_TOPIC] = {
            ConfigConstants.FROM_EMAIL: ConfigConstants.EMAIL_DEFAULT,
            ConfigConstants.TO_EMAIL: ConfigConstants.EMAIL_DEFAULT2,
            'password': 'your_password',
        }
        config['telegram'] = {
            'bot_token': 'INSERT_YOUR_BOT_TOKEN',
            'username': 'ExampleUser'
        }
        # Write config to file
        with open(config_path, 'w', encoding='utf-8') as config_file:
            config.write(config_file)
        sys.exit(0)

    # Write config to file
    with open(config_path, 'w', encoding='utf-8') as config_file:
        config.write(config_file)

    return config
