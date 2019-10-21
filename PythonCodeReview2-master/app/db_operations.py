import sqlite3


class DatabaseHandler:
    def __init__(self, database_name):
        self.database_name = database_name

    def get_data(self, date):
        with sqlite3.connect(self.database_name + '.db') as conn:
            cur = conn.cursor()
            cur.execute('SELECT currency_rates.usd, currency_rates.rub, currency_rates.gbp '
                        'FROM currency_rates WHERE currency_rates.dt=:date', {'date': date})
            row = cur.fetchone()
            if row is not None:
                rates = dict()
                rates['USD'] = row[0]
                rates['RUB'] = row[1]
                rates['GBP'] = row[2]
                return rates
            return None

    def insert_data(self, rates, date):
        with sqlite3.connect(self.database_name + '.db') as conn:
            cur = conn.cursor()
            cur.execute('INSERT INTO currency_rates (dt, usd, rub, gbp) VALUES (:dt, :usd, :rub, :gbp)',
                        {'dt': date, 'usd': rates['USD'], 'rub': rates['RUB'], 'gbp': rates['GBP']})
            conn.commit()


