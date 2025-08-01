# InSQL

[![PyPI Version](https://img.shields.io/pypi/v/insql)](https://pypi.org/project/insql/)
[![Python Versions](https://img.shields.io/pypi/pyversions/insql)](https://pypi.org/project/insql/)
[![License](https://img.shields.io/pypi/l/insql)](https://github.com/IntealDev/InSQL/blob/main/LICENSE)

**InSQL** — это легковесная SQL-подобная база данных, реализованная на чистом Python. Она предназначена для простых проектов, где не требуется полноценная СУБД, но нужна структурированное хранение данных с поддержкой транзакций, индексов и безопасного доступа.

## Ключевые особенности

- 🚀 **Простота**: Не требует сервера или дополнительных зависимостей.
- 📂 **Работа с файлами**: Данные хранятся в локальных файлах с расширением `.insql`.
- 🔒 **Безопасность**: Поддержка транзакций и контроль доступа к БД.
- 🔍 **Индексы**: Поддержка B-деревьев и хэш-индексов для быстрого поиска.
- 🐍 **Чистый Python**: Только стандартная библиотека (Python 3.6+).

## Установка

Установите InSQL через pip:

```bash
pip install insql