import app
import argparse
# noinspection PyBroadException


def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--telegram', help='Token of your telegram bot.', type=str, required=True)
    parser.add_argument('-f', '--fixer', help='Token of your fixer account.', type=str, required=True)
    parser.add_argument('-n', '--database_name', help='Name of your database', type=str, required=True)
    return parser.parse_args()


def main():
    tokens = get_arguments()
    app.init_bot(tokens.telegram.strip(), tokens.fixer.strip(), tokens.database_name.strip())
    app.bot.polling(none_stop=True, interval=1)


if __name__ == '__main__':
    main()
