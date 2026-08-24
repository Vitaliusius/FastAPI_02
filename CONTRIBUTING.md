# Разработчикам бэкенда

[TOC]

## Как развернуть локально

### Необходимое ПО

Для запуска ПО вам понадобятся консольный Git и Make. Инструкции по их установке ищите на
официальных сайтах:

- [Git SCM](https://git-scm.com/)
- [GNU Make](https://www.gnu.org/software/make/)

Вы можете проверить, установлены ли эти программы с помощью команд:
```shell
$ git --version
git version 2.37.1.windows.1

$ make --version
GNU Make 4.4.1
Built for Windows32
<...>
```

Для тех, кто использует Windows необходимы также программы **git** и **git bash**. В **git bash** необходимо дополнительно установить
**make**:

- Перейдите на сайт [ezwinports](https://sourceforge.net/projects/ezwinports/files/)
- Скачайте `make-4.4.1-without-guile-w32-bin.zip` (выберите версию без `guile`)
- Извлеките архив
- Скопируйте содержимое архива в `C:\ProgramFiles\Git\mingw64\` **БЕЗ** перезаписи/замены любых вложенных файлов.

Все дальнейшие команды запускать из-под **git bash**.

### Создание виртуального окружения для работы с IDE

IDE для корректной работы подсказок необходимо развернуть виртуальное окружение со всеми установленными зависимостями.

В качестве пакетного менеджера на проекта используется [uv](https://docs.astral.sh/uv/).

[Установите uv](https://gitlab.dvmn.org/root/fastapi-articles/-/wikis/Uv-package-manager#1-%D1%83%D1%81%D1%82%D0%B0%D0%BD%D0%BE%D0%B2%D0%BA%D0%B0-uv) и в корне репозитория выполните команду

```shell
$ uv sync
```

[uv](https://docs.astral.sh/uv/) создаст виртуальное окружение, установит необходимую версию Python и все необходимые зависимости.

После этого активируйте виртуальное окружение в текущей сессии терминала:

```shell
$ source .venv/bin/activate  # для Linux
$ .\.venv\Scripts\activate  # Для Windows
```

### Настройка pre-commit хуков

В репозитории используются хуки [pre-commit](https://pre-commit.com/), чтобы автоматически запускать линтеры и автотесты.

В корне репозитория в **активированном виртуальном окружении** запустите команду для настройки хуков:

```shell
$ pre-commit install
pre-commit installed at .git/hooks/pre-commit
```

В последующем при коммите автоматически будут запускаться линтеры и другие проверки. Если проверки не пройдут, то коммит прервётся с ошибкой.

Если вам потребуется сделать коммит без проверок, то вы можете отключить их с помощью флага `--no-verify`:
```shell
git commit -m 'Message' --no-verify
```

## Как вести разработку

Код проекта находится в папке `/src`.

Находясь в корневой директории проекта, запустить проект можно командой:

```shell
$ fastapi dev src/main.py
```

Проект будет работать по адресу http://127.0.0.1:8000/

### Как установить python-пакет в виртуальное окружение

В качестве менеджера пакетов используется [uv](https://docs.astral.sh/uv/).

Вот пример как добавить в зависимости библиотеку `beautifulsoup4`.

```shell
$ uv add beautifulsoup4
```

Конфигурационные файлы `pyproject.toml` и `uv.lock` обновятся автоматически.

Аналогичным образом можно удалять python-пакеты:

```shell
$ uv remove beautifulsoup4
```

Если необходимо обновить `uv.lock` вручную, то используйте команду:

```shell
$ uv lock
```

### Команды для быстрого запуска с помощью make

Для вывода списка часто используемых коротких команд используйте команду

```shell
$ make list
...
```
## Архитектура и схемы приложения

Перед внесением изменений ознакомьтесь со схемами архитектуры:
- [Схема: Локальная инсталляция бэкенда](https://gitlab.dvmn.org/root/fastapi-articles/-/wikis/fastai/backend_local_installation.drawio.png)
- [Схема: Prod инсталляция бэкенда](https://gitlab.dvmn.org/root/fastapi-articles/-/wikis/fastai/backend_prod_installation.drawio.png)
- [Схема: Декомпозиция бэкенда по подсистемам](https://gitlab.dvmn.org/root/fastapi-articles/-/wikis/fastai/backend_decomposition.drawio.png)

## Подключение фронтенда для локальной разработки

1. Скачайте архив со скомпилированным фронтендом из материалов проекта.
2. Распакуйте его в корень репозитория в папку `frontend/`.
3. Создайте файл `frontend/frontend-settings.json` с содержимым:
```
{
  "backendBaseUrl": "/frontend-api"
}
```
4. Добавьте папку с фронтендом `/frontend` в ` .gitignore`
5. Запустите сервер командой `fastapi dev src/main.py`.

## Настройка и запуск MinIO S3

Для локальной разработки используется MinIO — S3-совместимое объектное хранилище.

### 1. Установка MinIO

* **Windows:**
  Скачайте бинарный файл `minio.exe` с [официального сайта MinIO](https://dl.min.io/server/minio/release/windows-amd64/minio.exe) и поместите его в рабочую директорию.

### 2. Запуск сервера
Запустите сервер с указанием корневых учетных данных и каталога для данных:
```
set MINIO_ROOT_USER=admin
set MINIO_ROOT_PASSWORD=password123
minio.exe server minio_data --console-address ":9001" --address ":9000"
```

Откройте панель управления MinIO Console: http://localhost:9001 (логин: admin, пароль: password123).
Создайте бакет с именем sites (если он еще не создан).
Установите политику доступа бакета в режим Public (или через настройки бакета: Access Policy -> Public).
#### Ручная выгрузка 
Вручную положите в бакет файлы-заглушки:
Загрузите файл index.html (дефолтная HTML-страница).
Загрузите файл index.png (или screenshot.png для превью сайта).
Важно:
В коде бэкенда для html_url и screenshot_url должны использоваться прямые публичные ссылки на эти файлы (например, http://localhost:9000/sites/index.html и http://localhost:9000/sites/index.png).
Без рабочих ссылок на эти файлы фронтенд будет выглядеть сломанным (не отобразятся превью и карточки сайтов).

#### Программная выгрузка файлов в S3 (MinIO) из Python-кода

При сохранении сгенерированных страниц и скриншотов через Python-клиент (`aioboto3` / `boto3`) необходимо явно передавать параметры метаданных при вызове `put_object`:

1. **Параметр `ContentDisposition='inline'`**:
   Обязательно указывайте `ContentDisposition='inline'`, чтобы файл при переходе по ссылке открывался и рендерился напрямую в браузере, а не сохранялся на диск.

2. **MIME-типы (`ContentType`)**:
   Обязательно задавайте точный MIME-тип в зависимости от формата загружаемого файла:
   * Для HTML-файлов (`index.html`): `ContentType='text/html'`
   * Для изображений/скриншотов (`index.png`, `screenshot.png`): `ContentType='image/png'`

Пример кода выгрузки:

```python
# Выгрузка HTML-страницы
await s3_client.put_object(
    Bucket=bucket_name,
    Key="index.html",
    Body=html_content.encode("utf-8"),
    ContentType="text/html",
    ContentDisposition="inline",
)

# Выгрузка скриншота
await s3_client.put_object(
    Bucket=bucket_name,
    Key="index.png",
    Body=screenshot_bytes,
    ContentType="image/png",
    ContentDisposition="inline",
)
```
### 3.Настройка бакета
- Откройте веб-консоль MinIO по адресу http://localhost:9001.

- Авторизуйтесь с логином admin и паролем password123.

- Создайте новый бакет с именем sites.

- Установите политику доступа бакета (Access Policy) в значение Public (или Read-Only).

### 4. Переменные окружения (.env)
Укажите параметры подключения в вашем .env:
```
S3_ENDPOINT_URL=http://localhost:9000
S3_BUCKET_NAME=sites
S3_ACCESS_KEY=admin
S3_SECRET_KEY=password123
```
