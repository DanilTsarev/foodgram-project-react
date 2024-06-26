# Kitchen boy

[Описание](#описание) | [Технологии](#технологии) | [Запуск проекта](#запуск-проекта) | [Лицензия](#лицензия) | [Контакты](#контакты) | [Заголовок новый](#заголовок-новый)

## Описание
Kitchen boy - это веб-приложение для обмена рецептами и создания списков покупок. Пользователи могут делиться своими рецептами, добавлять рецепты в избранное, и корзину покупок, следить за другими пользователями и многое другое.
На сайте можно выполнять следующие действия:
- Для неавторизованных пользователей:
    - Доступна главная страница.
    - Доступна страница отдельного рецепта.
    - Доступна и работает форма авторизации.
    - Доступна и работает форма регистрации.
- Для авторизованных пользователей:
    - Доступна главная страница.
    - Доступна страница другого пользователя.
    - Доступна страница отдельного рецепта.
    - Доступна страница «Мои подписки».
    - Доступна страница «Избранное».
    - Доступна страница «Список покупок».
    - Доступна страница «Создать рецепт».
    - Доступна возможность выйти из системы.

## Технологии
Проект разработан с использованием следующих технологий и инструментов:

- Python 3.9
- Node.js
- Django 3.2
- Django Rest Framework (DRF)
- PostgreSQL
- Docker
- Nginx

## Запуск проекта
- Склонируйте репозиторий:
  ```
  git clone git@github.com:DanilTsarev/foodgram-project-react.git
  ```
- Создайте и активируйте виртуальное окружение:
- Установите зависимости из файла requirements.txt
- Примените миграции.
- Из корневой директории запустите команду через терминал WSL или другой Linux терминал:
  ```
  docker compose up --build
  ```

## Лицензия
Проект лицензирован под MIT License.

## Контакты
Если у вас возникли вопросы или предложения, свяжитесь со мной:
- Email: drsif@yandex.ru
- GitHub: [DanilTsarev](https://github.com/DanilTsarev)
