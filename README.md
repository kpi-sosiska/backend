# backend

# Установка

Пж загуглите команды если вы их не шарите

`git clone https://github.com/kpi-sosiska/backend`  
`pip install -r requirements.txt`


# Запуск

### Запуск админки:  
```python manage.py runserver```

Админка доступна по адресу http://127.0.0.1:8000/garni_studenti/admin/


### Запуск бота:

Бот подтягивает токен из environment variables.  
Их можно установить в PyCharm в конфигурации запуска или писать каждый раз при при запуске.

#### Лонгпол:
```bot_token=111111111:AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA python manage.py bot```

#### Вебхук:
```bot_token=111111111:AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA bot_port=8888 python manage.py bot --webhook```  

Подразумевается что бот лежит под нгинксом с ссл сертом.


# Структура

## mainapp
 Содержит модели БД и админку
 
## botapp
  апка с тг ботом (аиограм)  
  botapp/management/commands/bot.py позволяет запускать бота используя manage.py  
  на момент написания бот умеет только проводить опрос.  
  todo постить результаты в каналы
  
  
## parserapp
  Когда то будет тянуть расписание с kpi_rozklad
  