from app import bot, api_bot, supported_currencies
from datetime import datetime, timedelta
import math
import numpy as np
from scipy.interpolate import interp1d
from matplotlib import pyplot as plt
import calendar


@bot.message_handler(commands=['start'])
def handler_start(message):
    bot.send_message(message.chat.id, 'Привет, я умею писать текущие курсы валют и говорить о динамике цен валют!')


@bot.message_handler(commands=['help'])
def handler_start(message):
    bot.send_message(message.chat.id, 'Поддерживаемые команды:\n0) /currencies список поддерживаемой валюты.\n'
                                      '1) /latest_rates Текущий курс валют относительно какой-то валюты.\n'
                                      '2) /historical_rates Курс валют относительно другой валюты в какую-то дату.\n'
                                      '3) /historical_rates_cut Курс валюты относительно другой валюты через '
                                      'определенный промежуток времени.')


@bot.message_handler(commands=['currencies'])
def handler_start(message):
    bot_response = ['Список поддерживаемой валюты:\n', ', '.join(sorted(supported_currencies)), '.']
    bot.send_message(message.chat.id, ''.join(bot_response))


@bot.message_handler(commands=['latest_rates'])
def handler_current_rates(message):
    bot.send_message(message.chat.id, 'Введите валюту, относительно которой курсы вы хотите получать курсы, '
                                      'имя валюты должно быть либо в форме сокращения из 3 букв. В большинстве случаев '
                                      'вам нужно ввести RUB.')
    bot.register_next_step_handler(message, lambda m: get_base_currency(m, 'latest'))


@bot.message_handler(commands=['historical_rates'])
def handler_current_rates(message):
    bot.send_message(message.chat.id, 'Введите год, за который вы хотите узнать курсы валют.')
    bot.register_next_step_handler(message, lambda m: get_year(m, 'historical'))


@bot.message_handler(commands=['historical_rates_cut'])
def handler_current_rates(message):

    bot.send_message(message.chat.id, 'Введите год, начиная с которого вы хотите узнавать курсы валют.')
    bot.register_next_step_handler(message, lambda m: get_year(m, 'historical_cut'))


def get_year(message, getter_type):
    year = message.text.strip()
    if len(year) != 4 or not year.isdigit():
        bot.send_message(message.chat.id, 'Получен некорректный год.')
        return
    year = int(year)
    bot.send_message(message.chat.id, 'Введите номер месяца, начиная с которого вы хотите узнавать курсы валют.')
    bot.register_next_step_handler(message, lambda m: get_month(m, getter_type, [year]))


def get_month(message, getter_type, start_date):
    month = message.text.strip()
    if len(month) > 2 or not month.isdigit() or not 1 <= int(month) <= 12:
        bot.send_message(message.chat.id, 'Месяц введен некорректно.')
        return
    month = int(month)
    start_date.append(month)
    bot.send_message(message.chat.id, 'Введите день, начиная с которого вы хотите узнавать курсы валют.')
    bot.register_next_step_handler(message, lambda m: get_day(m, getter_type, start_date))


def correct_day(year, month, day):
    return calendar.monthrange(year, month)[1] >= day


def get_day(message, getter_type, start_date):
    day = message.text.strip()
    if len(day) > 2 or not day.isdigit() or day.isdigit() and not correct_day(start_date[0], start_date[1], int(day)):
        bot.send_message(message.chat.id, 'День введен некорректно.')
        return
    day = int(day)
    start_date.append(day)
    start_date = datetime(start_date[0], start_date[1], start_date[2], 0, 0, 0)
    if getter_type == 'historical':
        bot.send_message(message.chat.id, 'Введите валюту, относительно которой курсы вы хотите получать курсы, '
                                          'имя валюты должно быть либо в форме сокращения из 3 букв. В большинстве '
                                          'случаев вам нужно ввести RUB.')
        bot.register_next_step_handler(message, lambda m: get_base_currency(m, getter_type,
                                                                            start_date))
    elif getter_type == 'historical_cut':
        bot.send_message(message.chat.id, 'Введите разницу в днях, с которой дата будет увеличиваться.')
        bot.register_next_step_handler(message, lambda m: get_day_dif(m, getter_type, start_date))


def get_day_dif(message, getter_type, start_date):
    day_dif = message.text.strip()
    if not day_dif.isdigit() or day_dif.isdigit() and int(day_dif) == 0:
        bot.send_message(message.chat.id, 'Разница введена некорректно.')
        return
    day_dif = int(day_dif)
    bot.send_message(message.chat.id, 'Введите максимальное число запросов, которые вы хотите сделать (может быть '
                                      'сделано меньше запросов, если дата после какого-то запроса больше текущей).')
    bot.register_next_step_handler(message, lambda m: get_max_queries(m, getter_type, start_date, day_dif))


def get_max_queries(message, getter_type, start_date, day_dif):
    max_queries = message.text.strip()
    if not max_queries.isdigit() or max_queries.isdigit() and int(day_dif) == 0:
        bot.send_message(message.chat.id, 'Число запросов введено некорректно.')
        return
    max_queries = int(max_queries)
    bot.send_message(message.chat.id, 'Введите валюту, относительно которой курсы вы хотите получать курсы, '
                                      'имя валюты должно быть либо в форме сокращения из 3 букв. В большинстве случаев '
                                      'вам нужно ввести RUB.')
    bot.register_next_step_handler(message, lambda m: get_base_currency(m, getter_type, start_date, day_dif, max_queries))


def get_base_currency(message, getter_type, start_date=None, date_dif=None, max_queries=None):
    base_currency = message.text.upper()
    if len(base_currency) != 3 or base_currency not in supported_currencies:
        bot.send_message(message.chat.id, 'Не могу найти такую валюту.')
        return
    if getter_type != 'historical_cut':
        bot.send_message(message.chat.id, 'Курсы каких валют вы хотите узнать? Запишите валюты в виде трехбуквенного '
                                          'сокращения через запятую.')
    else:
        bot.send_message(message.chat.id, 'Курсы какой валюты вы хотите узнать?')
    bot.register_next_step_handler(message, lambda m: get_currency_rates(m, base_currency, getter_type, start_date,
                                                                         date_dif, max_queries))


def correct_currency_list(currency_list):
    for currency in currency_list:
        if currency not in supported_currencies:
            return False
    return True


def plot_graph(base_currency, currency, dates, values, number_of_days):
    precise_grid = np.linspace(int((dates[0] - datetime(1970, 1, 1)).total_seconds()),
                               int((dates[-1] - datetime(1970, 1, 1)).total_seconds()), num=10 * number_of_days)
    f = interp1d(list(map(lambda d: int((d - datetime(1970, 1, 1)).total_seconds()),
                          dates)), values, 'cubic')
    prediction = f(precise_grid)
    min_value, max_value = math.floor(min(prediction) * 100) / 100, math.ceil(max(prediction) * 100) / 100
    beautiful_precise_grid = list(map(lambda d: datetime.fromtimestamp(d).strftime('%d.%m.%y'), precise_grid))
    plt.figure(figsize=(10, 9))
    grid_step = math.floor(len(precise_grid) / 30)
    plt.plot(precise_grid, prediction, label=currency)
    beautiful_precise_grid = beautiful_precise_grid[::grid_step]
    prev = beautiful_precise_grid[0]
    for i in range(1, len(beautiful_precise_grid)):
        if beautiful_precise_grid[i] == prev:
            prev = beautiful_precise_grid[i]
            beautiful_precise_grid[i] = ''
        else:
            prev = beautiful_precise_grid[i]
    plt.xticks(precise_grid[::grid_step], beautiful_precise_grid, rotation=45)
    y_ticks = np.linspace(min_value, max_value, num=len(beautiful_precise_grid))
    plt.yticks(y_ticks)
    plt.ylabel(base_currency)
    plt.title('Курсы обмена по отношению к ' + base_currency)
    plt.legend()
    plt.grid(linestyle=':', alpha=0.5)
    plt.savefig('graph.png')
    plt.clf()


def get_currency_rates(message, base_currency, getter_type, date=None, days_dif=None, max_queries=None,
                       currencies=None, send_message=True):
    if getter_type == 'latest' or getter_type == 'historical':
        currency_list = currencies
        if currencies is None:
            currency_list = list(map(lambda s: s.upper().strip(), message.text.split(',')))
            currency_list.append(base_currency.upper())
            if not correct_currency_list(currency_list):
                bot.send_message(message.chat.id, 'Введенная валюта не поддерживается.')
                return
        if date is not None:
            date = date.strftime('%Y-%m-%d')
        api_bot_response = api_bot.get_current_rate(currency_list, date)
        success, currency_exchange_rates = api_bot_response[0], api_bot_response[1]
        if success:
            bot_response = ['Курсы обмена валют к ', base_currency, ':']
            for currency, exchange_rate in currency_exchange_rates.items():
                bot_response.append('\n')
                bot_response.append(currency)
                bot_response.append(' ')
                bot_response.append(str(round(exchange_rate, 3)))
            if send_message:
                bot.send_message(message.chat.id, ''.join(bot_response))
        else:
            errors_dict = dict(currency_exchange_rates)
            bot_response = ['Код ошибки ', str(errors_dict['code']), '\n', 'Описание ошибки: ', errors_dict['type']]
            bot.send_message(message.chat.id, ''.join(bot_response))
            with open('bug_fix_incoming.png', 'rb') as bug_fix_incoming:
                bot.send_photo(message.chat.id, bug_fix_incoming)
            bot.send_message(message.chat.id, 'Наши специалисты уже приступили к исправлению бага!')
        return api_bot_response
    if getter_type == 'historical_cut':
        currency_list = list(map(lambda s: s.upper().strip(), message.text.split(',')))
        currency_list.append(base_currency)
        if not correct_currency_list(currency_list) or len(currency_list) != 2:
            bot.send_message(message.chat.id, 'Введенная валюта не поддерживается.')
            return
        values = []
        dates = []
        while max_queries > 0 and date < datetime.now():
            success, currency_exchange_rates = get_currency_rates(message, base_currency, 'historical',
                                                                  date=date,
                                                                  currencies=currency_list, send_message=False)
            if not success:
                return
            for currency, value in currency_exchange_rates.items():  # словарь состоит лишь из 1 пары элементов
                values.append(value)
                dates.append(date)
            date += timedelta(days=days_dif)
            max_queries -= 1
        number_of_days = len(values)
        if number_of_days <= 3:
            output = ['Недостаточно данных для построения точного графика.', '']
            for date, value in zip(dates, values):
                output.append('Дата ' + date.strftime('%d.%m.%y') + ' , цена ' + str(round(value, 3)) + '.')
            bot.send_message(message.chat.id, '\n'.join(output))
            return
        plot_graph(base_currency, currency, dates, values, number_of_days)

        with open('graph.png', 'rb') as graph:
            bot.send_photo(message.chat.id, graph)

