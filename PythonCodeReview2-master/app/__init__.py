import telebot
import requests
from app import API
from app import db_operations

bot = None
api_bot = None
supported_currencies = None


# noinspection PyBroadException


def init_bot(bot_token, api_token, database_name):
    global bot
    bot = telebot.TeleBot(bot_token)
    database_bot = db_operations.DatabaseHandler(database_name)
    global api_bot
    api_bot = API.ApiBot(api_token, database_bot)
    get_supported_currencies_url = 'http://data.fixer.io/api/latest?access_key=' + api_token
    try:
        global supported_currencies
        supported_currencies = set(requests.get(get_supported_currencies_url).json()['rates'].keys())
    except Exception:
        print('Не удалось создать бота.')
    from app import handlers
