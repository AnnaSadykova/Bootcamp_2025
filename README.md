# Nexign Bootcamp API Tests

## Описание проекта
Набор тестов для проверки API системы биллинга. Тесты покрывают основные endpoints для работы с балансом, тарифами, аутентификацией и уведомлениями.

## Установка и настройка

Склонируйте к себе репозиторий, в котором хранится проект тестового задания, через выполнение команды в терминале

```bash
git clone https://github.com/AnnaSadykova/Bootcamp_2025.git
cd Bootcamp_2025
```

Убедитесь, что на Вашем компьютере установлен Python. В командной строке/терминале выполните команду, которая должна вернуть текущую версию питона на вашем компьютере:

```bash
python -v
```

Если версия не вывелась в консоли, то установите питон с официального сайта [Python](https://www.python.org/downloads/).

В процессе установки обязательно поставьте галочку в чекбоксе "Add python.exe to PATH". Иначе, у Вас могут быть проблемы с запуском Python

</br>
Установите необходимые зависимости из файла
requirements.txt для корректной работы скриптов, выполнив команду:

```bash
pip install -r requirements.txt
```

Если она не выполняется, то попробуйте по-другому:

```bash
pip3 install -r requirements.txt
```

## Запуск тестов

### Запуск всех тестов

```bash
python -m pytest tests/ -v
```

или

```bash
pytest tests/ -v
```

### Запуск тестов по категориям

Генератор позитивных cdr-файлов
```bash
pytest  tests/generators/positive_cdr_generator.py -v
```
Генератор негативных cdr-файлов
```bash
pytest  tests/generators/negative_cdr_generator.py -v
```
Тесты файлов e2e
```bash
pytest  tests/e2e/test.py -v
```
Тесты файлов CDR (валидатор)
```bash
pytest  tests/cdr/test.py -v
```
Тесты аутентификации
```bash
pytest tests/api/{subscriber,manager}_auth.py -v
```
Тесты работы с балансом
```bash
pytest tests/api/{get,put}_balance.py -v
```
Тесты работы с тарифами
```bash
pytest tests/api/{get_tariff_info,change_tariff}.py -v
```
Тесты уведомлений
```bash
pytest tests/api/send_SMS.py -v
```
Запуск конкретного теста
```bash
pytest tests/api/get_balance.py::test_get_balance -v
```

## Структура проекта
```
Bootcamp_2025/
├── pytest.ini            # Конфигурация pytest
├── requirements.txt      # Зависимости Python
├── tests/
│   ├── api/              # Тесты API
│   │   ├── constants.py  # Константы для тестов
│   │   ├── helpers.py    # Вспомогательные функции
│   │   ├── __init__.py
│   │   └── ...           # Файлы с тестами
│   ├── cdr/              # Тесты CDR
│   │   ├── helpers.py    # Вспомогательные функции
│   │   ├── __init__.py
│   │   └── test.py       # Файл с тестами CDR
│   ├── e2e/              # Тесты e2e
│   │   ├── helpers.py    # Вспомогательные функции
│   │   ├── __init__.py
│   │   └── test.py       # Файл с тестами e2e
│   ├── generators/       # Генераторы CDR
│   │   ├── negative_cdr_generator.py    # Порождение негативных CDR файлов
│   │   ├── positive_cdr_generator.py    # Порождение позитивных CDR файлов
│   │   └── __init__.py
│   ├── __init__.py
│   └── main.py           # Точка входа для запуска тестов
└── README.md             # Эта документация
```

## Дополнительные команды
Запуск тестов с логированием
```bash
pytest tests/ -v --log-level=DEBUG
```
Запуск только упавших тестов
```bash
pytest --lf -v
```