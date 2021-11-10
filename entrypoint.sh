#!/bin/bash

if [[ -v BOT_TOKEN ]]; then
    if [[ -v BOT_DOMAIN ]]; then
        gunicorn --workers 1 --timeout 120 --bind unix:/run/telegram_bot.sock botapp:gunicorn --worker-class aiohttp.GunicornWebWorker --capture-output
    else
        python manage.py bot
    fi
elif [ "$ADMIN" == "PROD" ]; then
    python manage.py collectstatic --no-input
    gunicorn --workers 4 --bind unix:/run/django_admin.sock garni_studenti.wsgi:application --capture-output
elif [ "$ADMIN" == "DEV" ]; then
    python manage.py runserver 0.0.0.0:8000
else
    echo "You must set BOT_TOKEN to run bot or ADMIN to run django admin"
fi
