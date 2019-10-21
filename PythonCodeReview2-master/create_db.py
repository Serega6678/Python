import sqlite3
import argparse


def create_table(args):
    with sqlite3.connect(args.database_name + '.db') as conn:
        cur = conn.cursor()
        cur.execute(
            '''CREATE TABLE IF NOT EXISTS currency_rates (dt VARCHAR(10) PRIMARY KEY, usd REAL, rub REAL, gbp REAL)''')
        conn.commit()


def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--database_name', help='Database name.', required=True, type=str)
    return parser.parse_args()


def main():
    args = get_arguments()
    create_table(args)


if __name__ == "__main__":
    main()
