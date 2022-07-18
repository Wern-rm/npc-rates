# NCP Rates - Сервис управления курсами валют

![Image alt](https://img.shields.io/badge/python-%203.10-blue)
![Image alt](https://img.shields.io/badge/current%20version-1.0.0-green)
![Image alt](https://img.shields.io/badge/Developer-WeRn-red)

### Инструкция по запуску:
****

**Запуск сервиса осуществляется через docker-compose:**
```
 docker-compose up -d --build
```

### Описание системы:
****
**create_db - создает базу данныз sqlite3**
```
/create/db
```
**update_rates - Получение данных о курсах валют из НЦ РБ по указанной дате и сохранение полученных данных в базе данных**
```
/update/rates?date={}
```
**rate - Возвращает текущий курс валют по указанному коду валюты и даты**
```
/rate?currency_id={}&date={}
```
