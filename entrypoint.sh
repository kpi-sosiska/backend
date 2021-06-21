#!/bin/bash

if [[ -v BOT_TOKEN ]]; then
    gunicorn --workers 1 --bind unix:/run/telegram_bot.sock botapp:gunicorn --worker-class aiohttp.GunicornWebWorker --capture-output
elif [[ -v ADMIN ]]; then
    gunicorn --workers 4 --bind unix:/run/django_admin.sock garni_studenti.wsgi:application --capture-output
else
    echo "You must set BOT_TOKEN to run bot or ADMIN to run django admin"
fi