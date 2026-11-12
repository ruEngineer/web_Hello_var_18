# web_Hello_var_18 — «Заказ билетов» (вариант 18), задача Z1

Задача Z1 по дисциплине «Программирование на языке Python» (Python 2): web-проект `web_Hello_var_18` с приложением `firstapp_var_18` на Django. Данные хранятся в файлах txt/xlsx в папке `tablica`, база данных не используется.

Ниже README идёт по шагам задания: введение, задачи 1.1, 1.2 и 1.3. В конце — запуск.

---

## Иерархия проекта (как в лекции 2)

```
web_Hello_var_18/                 проект PyCharm с виртуальной средой
├── .venv/                        виртуальная среда
├── requirements.txt              пакеты для .venv
├── run.bat                       запуск одним щелчком
├── README.md
└── web_Hello_var_18/             web-проект (django-admin startproject web_Hello_var_18)
    ├── manage.py
    ├── web_Hello_var_18/         пакет web-проекта
    │   ├── __init__.py
    │   ├── settings.py
    │   ├── urls.py
    │   └── wsgi.py
    ├── firstapp_var_18/          web-приложение (python manage.py startapp firstapp_var_18)
    │   ├── tablica/              txt- и xlsx-файлы с данными
    │   ├── __init__.py
    │   ├── apps.py
    │   ├── forms.py
    │   ├── tablica_io.py         чтение и запись файлов tablica
    │   ├── urls.py
    │   └── views.py
    ├── templates/
    │   └── firstapp_var_18/      шаблоны приложения: base.html, index.html и др.
    └── static/
        └── images/               logo.svg
```

В проекте оставлено только то, что используется на сайте. База данных не нужна (`DATABASES = {}` в `settings.py`), заготовки Django (`models.py`, `tests.py`, `migrations/`, `asgi.py`, `db.sqlite3`) удалены.

---

## Страницы сайта

Меню: «Расписание» (главная) и «Купить билет». Остальные страницы открываются по ссылкам со страниц сайта.

| Адрес | Функция | Шаблон | Откуда ссылка |
|---|---|---|---|
| `/` | `index` | `index.html` | меню «Расписание» |
| `/day/<1–7>/` | `routes_by_day` | `routes.html` | фильтр «Дни» в расписании |
| `/route/<номер>/` | `route_detail` | `route_detail.html` | номер рейса в расписании |
| `/buses/`, `/buses/<вид>/` | `buses` | `buses.html` | «Другие автобусы этого вида» на странице рейса |
| `/order/new/` | `order_new` | `order_form.html` | меню «Купить билет», «Купить» в расписании |
| `/order/done/?number=…` | `order_done` | `order_done.html` | после отправки формы |
| `/orders/` | `orders` | `orders.html` | «Все заказы» после оформления |

---

## Шаг 0. Введение: проект, приложение, настройки

| Требование | Что сделано |
|---|---|
| Проект с виртуальной средой | `.venv` в корне, пакеты перечислены в [requirements.txt](requirements.txt) |
| Модуль Django | `Django==6.1.2` (для xlsx-файлов — `openpyxl`) |
| Web-проект `web_Hello_var_18` | папка [web_Hello_var_18](web_Hello_var_18/web_Hello_var_18) (`settings.py`, `urls.py`) |
| Web-приложение `firstapp_var_18` | папка [firstapp_var_18](web_Hello_var_18/firstapp_var_18) |
| Приложение зарегистрировано | `INSTALLED_APPS` в [settings.py](web_Hello_var_18/web_Hello_var_18/settings.py) |
| Русский язык и другие настройки | `LANGUAGE_CODE = 'ru-ru'`, `TIME_ZONE = 'Europe/Moscow'` |
| Папки `templates` и `static` | `templates/` (`'DIRS': [BASE_DIR / 'templates']`), `static/` (`STATICFILES_DIRS`) |
| Шаблон `index.html` | [templates/firstapp_var_18/index.html](web_Hello_var_18/templates/firstapp_var_18/index.html) |
| Шаблон `navigator.html` | **не выполнено:** страница навигатора удалена, переходы идут через меню и ссылки на страницах |

Команды, которыми создаётся такая структура (лекции 1–2):

```bash
django-admin startproject web_Hello_var_18
cd web_Hello_var_18
python manage.py startapp firstapp_var_18
python manage.py runserver
```

Шаблоны лежат в папке с именем приложения (`templates/firstapp_var_18/`), как в лекции 2.

---

## Шаг 1. Задача 1.1 — представления и маршрутизация (views, urls)

Функции — [views.py](web_Hello_var_18/firstapp_var_18/views.py), маршруты — [urls.py](web_Hello_var_18/firstapp_var_18/urls.py).

| Требование | Адрес | Функция |
|---|---|---|
| Страницы по теме (6–8 штук) | 7 адресов из таблицы «Страницы сайта» | — |
| `path` с параметром | `/route/<int:number>/` | `route_detail` |
| `re_path` с регулярным выражением | `^day/(?P<day>[1-7])/$` | `routes_by_day` |
| Параметр по умолчанию | `/buses/` и `/buses/<str:kind>/` | `buses(request, kind='все')` |
| Параметры строки запроса | `/order/new/?route=115` (рейс выбран заранее), `/order/done/?number=1001` | `order_new`, `order_done` (`request.GET.get(...)`) |
| Переадресация | после отправки формы `/order/new/` → `/order/done/?number=…`; `/order/done/` без номера → `/order/new/` | `order_new`, `order_done` (`redirect`) |

Проверка ручным вводом: `/route/112/`, `/day/3/`, `/buses/пригородный/`, `/order/new/?route=115`. Неверный адрес, например `/day/8/`, вернёт 404.

---

## Шаг 2. Задача 1.2 — шаблоны (templates)

| Требование | Где |
|---|---|
| Простые данные разных типов (str, int, bool, date) | главная `/`, функция `index`: название, число рейсов, средняя цена, работают ли кассы, сегодняшняя дата |
| Сложные данные: список, кортеж, словарь | главная `/`: рейсы — список словарей из `routes.xlsx`, дни недели — словарь кортежей из `days.txt` (`day.0`, `day.1` в шаблоне), популярный рейс — словарь |
| Таблицы на страницах | `/`, `/day/<1–7>/`, `/route/<номер>/`, `/buses/`, `/orders/` |
| Папка `tablica` в приложении | [firstapp_var_18/tablica](web_Hello_var_18/firstapp_var_18/tablica) |
| Списки в текстовых файлах | `bus_types.txt` (16 строк, страница `/buses/`), `operators.txt` (15, список «Оператор» в форме), `days.txt` (7 дней недели, фильтр в расписании) |
| Таблицы `*.xlsx` с заголовками | `routes.xlsx` (16 рейсов, расписание), `orders.xlsx` (заказы, пополняется формой, страница `/orders/`) |
| Чтение файлов `tablica` | модуль [tablica_io.py](web_Hello_var_18/firstapp_var_18/tablica_io.py) (`read_txt`, `read_xlsx`) |
| Базовый шаблон `base.html` | [base.html](web_Hello_var_18/templates/firstapp_var_18/base.html) с блоками `title`, `header` и `content`; от него наследуются все страницы (`{% extends "firstapp_var_18/base.html" %}`) |
| Стили | вариант для PyCharm Community: стили написаны вручную в `<head><style>…</style></head>` файла `base.html` |
| Рисунки и изображения | логотип в шапке каждой страницы: `{% load static %}` и `<img src="{% static 'images/logo.svg' %}">` в `base.html`, файл в `static/images/` (как в лекции 2) |

---

## Шаг 3. Задача 1.3 — формы

| Требование | Где |
|---|---|
| Форма в `forms.py` | `TicketOrderForm` в [forms.py](web_Hello_var_18/firstapp_var_18/forms.py) |
| Простые данные | ФИО, телефон, дата поездки, количество мест |
| Одинарный выбор из списка | рейс и оператор (`select`), списки берутся из файлов `tablica` |
| Множественный выбор | дополнительные услуги: багаж, страховка (`checkbox`) |
| Запрос POST | `/order/new/`, функция `order_new` |
| Вывод на другой шаблон (GET) | после отправки — переход на `/order/done/?number=…` |
| Добавление в файл к уже имеющимся | новая строка дописывается в `tablica/orders.xlsx` (`append_order` в `tablica_io.py`) |
| День недели | вычисляется по дате поездки и записывается в `orders.xlsx` вместе с заказом |
| Проверки | телефон по шаблону (`RegexValidator`), дата не в прошлом (`clean_travel_date`), рейс ходит в день недели выбранной даты (`clean`) |

Форма выводится как в лекции 2: `<table>{{ form.as_table }}</table>` и кнопка `<input type="submit">`.

Если `orders.xlsx` открыт в Excel, Windows не даёт его перезаписать — форма покажет сообщение «файл открыт в другой программе». Закройте файл и отправьте форму ещё раз.

---

## Запуск

### Быстро: run.bat

Двойной щелчок по [run.bat](run.bat). Нужен установленный Python 3.12 или новее (с галочкой «Add python.exe to PATH»).

При первом запуске он создаст `.venv`, установит пакеты (нужен интернет) и проверит проект (`manage.py check`). Потом запустит сервер в отдельном окне и откроет в браузере главную страницу http://127.0.0.1:8000/ (расписание). Чтобы остановить сервер, закройте его окно.

- `run.bat setup` — только подготовка, без запуска сервера.

Если папка `.venv` скопирована с другого компьютера, `run.bat` остановится на установке пакетов: `.venv` ссылается на Python, которого на этом компьютере нет. Удалите папку `.venv` и запустите `run.bat` ещё раз — окружение создастся заново.

### Вручную

```bash
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
cd web_Hello_var_18
..\.venv\Scripts\python manage.py runserver
```

Открыть http://127.0.0.1:8000/ (расписание).
