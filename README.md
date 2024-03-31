# Foodgram

![Status workflow.](https://github.com/Anquientas/foodgram-project-react/actions/workflows/main.yml/badge.svg)

Проект представляет собой сайт, на котором пользователи публикуют свои рецепты, добавляют рецепты других авторов в избранное и подписываются на публикации других авторов.

Пользователям сайта также доступна функция «Список покупок». Она позволяет создавать список продуктов, которые нужно купить для приготовления добавленных в список блюд.

_Ссылка на [проект](http://foodgramus.ddns.net "Гиперссылка к проекту.")_

_Ссылка на [админку проекта](http://foodgramus.ddns.net/admin "Гиперссылка к админке Django.")_

_Ссылка на документацию [API](http://foodgramus.ddns.net/api/docs/ "Гиперссылка к API.") с актуальными адресами. Здесь описана структура возможных запросов и ожидаемых ответов_


## Стек проекта

Python, Django, Django REST Framework, PostgreSQL, Docker, JavaScript.React

Используемые библиотеки и пакеты для backend сохранены в файле backend/requirements.txt

## Как запустить проект на удаленном сервере

Для работы требуется:

- склонировать репозиторий проекта:

```
https://github.com/Anquientas/foodgram-project-react.git
```

- установить на сервере Docker и Docker Compose:
    + установить утилиту для скачивания файлов:

    ```
    sudo apt install curl
    ```

    + скачать скрипт для установки:
    
    ```
    curl -fsSL https://get.docker.com -o get-docker.sh
    ```

    + запустить скрипт установки:

    ```
    sh get-docker.sh
    ```

    + установить Docker Compose:
        
    ```
    sudo apt-get install docker-compose-plugin
    ```

- создать на сервере и заполнить файл ```.env``` параметрами, указанными в файле ```.env.example``` (см. подраздел "**Параметры .env**"), расположенный в корневой директории проекта;

- в разделе ***Secrets*** в настройках репозиотрия для работы ***GitHub Actions*** необходимо добавить следующие параметры:
    
    + пароль от Docker Hub (```DOCKER_PASSWORD```)
    
    + никнейм в Docker Hub (```DOCKER_USERNAME```)
    
    + публичный IP сервера (```HOST```)
    
    + закрытый SSH-ключ для доступа к серверу (```SSH_KEY```)
    
    + код доступа к серверу (если ssh-ключ защищен паролем)(```SSH_PASSPHRASE```)
    
    + Никнейм на сервере (```USER```)

- развертывание проекта на удаленном сервере можно выполнить двумя сопосбами:
    + запустить ***GitHub Action*** и ожидать окончания автоматического деплоя;
    
    + если запустить ***GitHub Action*** не удалось, то на удаленном сервере выполнить команды:

        * перейти в папку *infra* и скопировать на сервер в папку *infra* файлы ```docker-compose.production.yml``` и ```nginx.conf```:
        
        ```
        scp docker-compose.production.yml username@IP:/home/username/<дальнейший путь до папки проекта>/infra/docker-compose.production.yml
        ```

        ```
        scp nginx.conf username@IP:/home/username/<дальнейший путь до папки проекта>/infra/nginx.conf
        ```

        где:
        1. username - имя пользователя на сервере;
        2. IP - публичный IP сервера;

        * перейти в папку *docs* и скопировать на сервер в папку *docs* файлы ```openapi-schema.yml``` и ```redoc.html```:

        ```
        scp openapi-schema.yml username@IP:/home/username/<дальнейший путь до папки проекта>/docs/openapi-schema.yml
        ```

        ```
        scp redoc.html username@IP:/home/username/<дальнейший путь до папки проекта>/docs/redoc.html
        ```

        * скачать Docker-образы и создать необходимые Docker-контейнеры и volumes:
        
        ```
        sudo docker compose -f docker-compose.production.yml up -d
        ```

        * собрать статику (статические файлы) для Django-админки:
        
        ```
        sudo docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic --noinput
        ```

        * выполнить миграции:
        
        ```
        sudo docker compose -f docker-compose.production.yml exec backend python manage.py migrate
        ```

        * загрузить в базу данных (БД) заготовленные данные по тегами и продуктами:
        
        ```
        sudo docker compose -f docker-compose.production.yml exec backend python manage.py loaddata data/tags.json
        ```

        ```
        sudo docker compose -f docker-compose.production.yml exec backend python manage.py loaddata data/ingredients.json
        ```

    + создать суперпользователя (необходимо заполнить все запрашиваемые данные в диалоге в консоли):
    
    ```
    sudo docker compose -f docker-compose.production.yml exec backend python manage.py createsuperuser
    ```

### После каждого обновления репозитория (push в ветку master) будет происходить:

- проверка кода на соответствие стандарту ***PEP8*** (с помощью пакета ```flake8```)

- сборка и доставка Docker-образов ```frontend```,```backend``` и ```gateway``` на ***Docker Hub***

- разворачивание проекта на удаленном сервере

### После развертывания для работы в проекте предусмотрены следующие адреса:
    
- для проекта:

```
http://<ваше доменное имя или внешний IP-адрес удаленного сервера>/
```

- для админки проекта:

```
http://<ваше доменное имя или внешний IP-адрес удаленного сервера>/admin/
```

- для просмотра документации API:

```
http://<ваше доменное имя или внешний IP-адрес удаленного сервера>/api/docs/
```

## Как запустить проект локально

- склонировать репозиторий проекта:

```
https://github.com/Anquientas/foodgram-project-react.git
```

- установить Docker и Docker Compose (см. подраздел "**Как запустить проект на удаленном сервере**" для **Linux**. Для **Windows** достаточно установить программу ***Docker Desktop***)

- создать и заполнить файл ```.env``` параметрами, указанными в файле ```.env.example``` (см. подраздел "**Параметры .env**"), расположенном в корневой директории проекта;

- в папке *infra* в файле ```docker-compose.production.yml``` поменять запись 

```
  nginx:
    image: anquientas/foodgram_gateway
    env_file: ../.env
    depends_on:
      - backend
      - frontend
    ports:
      - 8000:80
```

на 

```
  nginx:
    image: anquientas/foodgram_gateway
    env_file: ../.env
    depends_on:
      - backend
      - frontend
    ports:
      - 80:80
```

- выполнить из папки *infra* команды, перечиленные для деплоя в случае невозможности автоматического деплоя (см. подраздел "**Как запустить проект на удаленном сервере**")

### После развертывания для работы в проекте предусмотрены следующие адреса:
    
- для проекта:

```
http://localhost:8000/
```

- для админки проекта:

```
http://localhost:8000/admin/
```

- для просмотра документации API:

```
http://localhost:8000/api/docs/
```

## Параметры .env

В файле .env.example содержатся следующие параметры:

- POSTGRES_DB
- POSTGRES_USER
- POSTGRES_PASSWORD
- DB_HOST
- DB_PORT
- SECRET_KEY
- ALLOWED_HOSTS

Параметр ```POSTGRES_DB```определяет имя базы данных

Параметр ```POSTGRES_USER```определяет имя пользователя, от лица которого происходит работа с БД

Параметр ```POSTGRES_PASSWORD```определяет пароль пользователя, указанного в ```POSTGRES_USER```, для доступа к БД

Параметр ```DB_HOST```определяет адрес, по которому Django будет соединяться с базой данных

Параметр ```DB_PORT```определяет порт, по которому Django будет обращаться к базе данных. 5432 — это порт по умолчанию для PostgreSQL

Параметр ```SECRET_KEY```содержит ***SECRET_KEY*** Django-проекта

Параметр ```ALLOWED_HOSTS```определяет адреса, у которых есть доступ к проекту. ***Разделительный символ при перечислении адресов - один пробел***

Дополнительно можено указать параметр ```DEBUG```, который определяет использование режима разработчика. По умлочанию - значение ***False***. Значение ***True*** включит режим отладки

## Авторы

Владимир Матасов ([GitHub](https://github.com/Anquientas/)) - разработка backend, API и deploy

Команда YandexPraktikum - разработка frontend и ревью
