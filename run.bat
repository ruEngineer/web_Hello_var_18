@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0"
title Заказ билетов — вариант 18 (Z1)

rem ============================================================
rem  Запуск задачи Z1: http://127.0.0.1:8000/
rem  Первый запуск сам создаёт .venv и ставит пакеты (нужен интернет).
rem  run.bat setup — только подготовка, без запуска сервера.
rem ============================================================

rem ---------- Python ----------
set "PY="
where py >nul 2>nul && set "PY=py -3"
if not defined PY where python >nul 2>nul && set "PY=python"
if not defined PY (
    echo [!] Python не найден. Установите Python 3.12 или новее с python.org
    echo     и отметьте при установке "Add python.exe to PATH".
    pause & exit /b 1
)

rem ---------- виртуальное окружение ----------
if not exist ".venv\Scripts\python.exe" (
    %PY% -c "import sys; sys.exit(0 if sys.version_info >= (3, 12) else 1)" || (
        echo [!] Нужен Python 3.12 или новее.
        pause & exit /b 1
    )
    echo Создаю виртуальное окружение .venv ...
    %PY% -m venv .venv || (echo [!] Не удалось создать .venv & pause & exit /b 1)
)
set "VPY=%CD%\.venv\Scripts\python.exe"

echo Проверяю пакеты из requirements.txt ...
"%VPY%" -m pip install -q --disable-pip-version-check -r requirements.txt || (
    echo [!] Не удалось установить пакеты. Проверьте подключение к интернету.
    echo     Если папка .venv скопирована с другого компьютера, удалите её и запустите run.bat ещё раз.
    pause & exit /b 1
)

rem ---------- дальше команды manage.py — из папки web-проекта ----------
cd web_Hello_var_18

rem ---------- проверка проекта (база данных в Z1 не используется) ----------
echo Проверяю проект ...
"%VPY%" manage.py check || (echo [!] Ошибка в проекте — подробности выше. & pause & exit /b 1)

if /i "%~1"=="setup" (
    echo Готово: окружение подготовлено.
    exit /b 0
)

rem ---------- запуск ----------
start "Z1 — http://127.0.0.1:8000" /d "%CD%" cmd /k ""%VPY%" manage.py runserver 8000"
timeout /t 3 /nobreak >nul
start "" "http://127.0.0.1:8000/"
echo.
echo Сервер запущен в отдельном окне: http://127.0.0.1:8000/
echo Чтобы остановить сервер, закройте его окно.
pause
exit /b 0
