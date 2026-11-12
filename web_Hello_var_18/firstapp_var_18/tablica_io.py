"""Чтение и запись данных из папки tablica (txt-списки и xlsx-таблицы)."""
from datetime import date
from threading import Lock
from django.conf import settings
from openpyxl import load_workbook

TABLICA_DIR = settings.TABLICA_DIR


def read_txt(name):
    """Возвращает список кортежей: каждая строка файла разбита по ';'."""
    path = TABLICA_DIR / name
    with open(path, encoding='utf-8') as f:
        return [tuple(line.strip().split(';')) for line in f if line.strip()]


def read_xlsx(name):
    """Возвращает (заголовки, строки) первого листа xlsx-файла."""
    wb = load_workbook(TABLICA_DIR / name, read_only=True)
    ws = wb.active
    rows = list(ws.iter_rows(values_only=True))
    wb.close()
    return list(rows[0]), [list(r) for r in rows[1:] if any(c is not None for c in r)]


def days():
    """Словарь: номер дня -> (полное название, краткое)."""
    return {num: (full, short) for num, full, short in read_txt('days.txt')}


def bus_types():
    return [{'name': n, 'seats': int(s), 'kind': k} for n, s, k in read_txt('bus_types.txt')]


def operators():
    return read_txt('operators.txt')


def routes():
    """Рейсы из routes.xlsx в виде списка словарей."""
    _, rows = read_xlsx('routes.xlsx')
    keys = ('number', 'from_city', 'to_city', 'departure', 'duration', 'price', 'bus', 'days')
    result = []
    for r in rows:
        item = dict(zip(keys, r))
        item['days_list'] = item['days'].split(',')
        result.append(item)
    return result


def find_route(number):
    return next((r for r in routes() if r['number'] == number), None)


def orders():
    return read_xlsx('orders.xlsx')


def find_order(number):
    header, rows = orders()
    for r in rows:
        if r[0] == number:
            return dict(zip(header, r))
    return None


_write_lock = Lock()


def append_order(data):
    """Добавляет заказ в конец orders.xlsx и возвращает его номер."""
    with _write_lock:  # runserver обрабатывает запросы в потоках — не даём двум запросам писать файл одновременно
        return _append_order(data)


def _append_order(data):
    path = TABLICA_DIR / 'orders.xlsx'
    wb = load_workbook(path)
    ws = wb.active
    numbers = [c.value for c in ws['A'][1:] if isinstance(c.value, int)]
    number = max(numbers, default=1000) + 1

    ws.append([
        number, date.today().isoformat(), data['passenger'], data['phone'], data['route'],
        data['travel_date'].isoformat(), '', data['seats'], data['total'],
        '', ', '.join(data['extras']),
    ])
    wb.save(path)
    return number