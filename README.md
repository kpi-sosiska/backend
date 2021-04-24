# backend

# Запуск

Бот подтягивает токен из environment variables.  
Их можно установить в PyCharm в конфигурации запуска или писать каждый раз при при запуске.

Запуск с указанием токена:  
```bot_token=111111111:AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA python manage.py runserver```  
Можно запускать и без токена, если бот не нужен.


На момент этого коммита бот работает только на вебхуках. Поставить вебхук можно так
```bot_token=111111111:AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA python manage.py bot --webhook 42.123.69.228```  
Для этого нужно иметь домен с сертификатом) Думаю стоит добавить поллинг.


Админка доступна по адресу http://127.0.0.1:8000/garni_studenti/admin/

# Структура

## mainapp
 Содержит модели БД и админку
 
## botapp
  апка с тг ботом (аиограм)  
  botapp/management/commands/bot.py позволяет (пока что нет) запускать бота используя manage.py  
  на момент написания бот умеет только проводить опрос.  
  todo постить результаты в каналы
  
  
## parserapp
  парсит преподов в бд.   
  использует api.rozklad.org.  
  в идеале надо парсить rozklad.kpi.ua, но то потом и в другой репе
