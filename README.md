# FastAPI Async Auth Service
Сервис аутентификации пользователей.

## Архитектура проекта
![AUTH](https://user-images.githubusercontent.com/103115934/283371673-b507ddca-4e39-4518-8980-41f79c963733.jpg)

## Краткое описание проекта
Проект реализует базовый функционал аутентификации:
- Регистрация
- Авторизация
- Аутентификация
- Разавторизация

### Принцип работы отдельных модулей:
#### Регистрация
При регистрации пользователь записывается в БД и получает уникальную сигнатуру. Эта сигнатура в будущем используется как уникальный идентификатор токена доступа (access_token). Хранится сигнатура в виде заголовка JTI в токене, со стороны сервиса каждая сигнатура хранится в БД, связью один к одному.

#### Авторизация
При авторизации пользовательская сессия сохраняется в БД, чтобы в будущем он мог узнать свою историю в личном кабинете. А также получает пару токенов - `access_token` и `refresh_token`. Стоит отметить, что `access_token` автоматически устанавливается в `http-only cookie`, a `refresh_token` сохраняется в БД для будущей валидации и выдачи новой сессии. Дальнейшее распознавание пользователя будет вестись именно куке. При помощи `refresh_token` юзер может получить новую пару JWT-токенов.

#### Аутентификация
Аутентификация пользователя происходит по куке, а также в отдельных случаях для защищенных частей сервиса придуман специальны роут - `/verify`. Он позволяет проверить - не были ли отозваны `access_token`-ы пользователя, если мы хотим удостовериться, что перед нами реальный пользователь, а не потенциальный злоумышленник.

#### Разавторизация
В нашем сервисе есть два типа разавторизации - конкретной сессии и всех сессий. При выходе из конкретной сессии удаляется кука и рефреш токен из БД, чтобы не было возможности его переиспользовать. При удалении всех сессий - удаляется кука, удаляются все `refresh_token`-ы выпущенные для пользователя, а также меняется сигнатура в БД, которая является идентифиакатором выпущенных `access`-токенов. Таким образом, если пользователь нажал на выход из всех сессий - все выпщуенные `access_token`-ы для этого пользователя становятся невалидными.

## Полезные команды
Поднятие композиции сервиса:
```shell
make up
```

Тестирование сервиса:
```shell
pytest
```

Локальное развертывание:
1. Установка зависимостей
```shell
make init
```
2. Запуск приложения
```shell
make run
```

Участники проекта:
- [Arina](https://github.com/sitdaria)
- [Alexandr](https://github.com/AlexanderZharyuk)
- [Vyacheslav](https://github.com/VyacheslavKazakov)

