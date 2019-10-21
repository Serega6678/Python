# PythonCodeReview2

Для создания базы данных, хранящей курсы валют по отношению к евро по датам, нужно перед запуском программы запустить скрипт create_db.py.
Запускать нужно лишь 1 раз, без запуска скрипта бот работать не будет. Пример запуска для моих токенов:

python create_db.py --database_name testing_base 

python run.py --telegram ** токен telegram бота ** --fixer ** токен fixer аккаунта ** --database_name testing_base

Для запуска бота нужно запустить скрипт run.py.
