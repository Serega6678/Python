import requests
from datetime import datetime

url = 'http://data.fixer.io/api/'
cached_currencies = ['USD', 'RUB', 'GBP']


class ApiBot:
    def __init__(self, token_name, database_bot):
        self.token = token_name
        self.database_bot = database_bot

    # noinspection PyMethodMayBeStatic
    def convert_currency_rates(self, base_currency_exchange_rate, other_currencies_rates):
        correct_currency_rates = dict()
        for rate in other_currencies_rates.items():
            correct_currency_rates[rate[0]] = base_currency_exchange_rate / rate[1]
        return correct_currency_rates

    # noinspection PyMethodMayBeStatic
    def incorrect_response(self, response):
        response_dictionary = response.json()
        success = response_dictionary['success']
        if success:
            return False
        return response_dictionary['error'].items()

    # noinspection PyMethodMayBeStatic
    def default_currencies(self, currencies):
        default_currencies_list = ['RUB', 'USD', 'GBP']
        for currency in currencies:
            if currency not in default_currencies_list:
                return False
        return True

    # noinspection PyMethodMayBeStatic
    def get_current_rate(self, currencies, date=None):
        correct_date = date
        if correct_date is None:
            correct_date = datetime.now().date().strftime('%Y-%m-%d')
        currencies_added = []
        for currency in cached_currencies:
            if currency not in currencies:
                currencies.append(currency)
                currencies_added.append(currency)
        rates = self.database_bot.get_data(correct_date)
        if self.default_currencies(currencies) and rates is not None:
            while len(currencies_added) > 0:
                del rates[currencies_added[-1]]
                currencies_added.pop()
                currencies.pop()
            base_currency_exchange_rate = rates[currencies[-1]]
            del rates[currencies[-1]]
            return [True, self.convert_currency_rates(base_currency_exchange_rate, rates)]
        request_type = 'latest'
        if date is not None:
            request_type = date
        temp_url = ''.join([url, request_type, '?access_key=', self.token, '&symbols=', ','.join(currencies)])
        response = requests.get(temp_url)
        incorrect_request = self.incorrect_response(response)
        if incorrect_request:
            return [False, incorrect_request]
        response_dictionary = response.json()['rates']
        #
        rates = dict()
        for currency in cached_currencies:
            rates[currency] = response_dictionary[currency]
            if currency in currencies_added:
                del response_dictionary[currency]
        if self.database_bot.get_data(correct_date) is None:
            self.database_bot.insert_data(rates, correct_date)
        while len(currencies_added) > 0:
            currencies_added.pop()
            currencies.pop()
        #
        base_currency_exchange_rate = response_dictionary[currencies[-1]]
        del response_dictionary[currencies[-1]]
        # api возвращает курсы только по отношению к EUR, этой функцией я перевожу их к базовой валюте
        return [True, self.convert_currency_rates(base_currency_exchange_rate, response_dictionary)]
