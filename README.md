# FastAI

## Репозиторий для бэкенд-разработчиков.

Инструкции и справочная информация по разворачиванию локальной инсталляции собраны
в документе [CONTRIBUTING.md](./CONTRIBUTING.md).

Требования к окружению: Python 3.13.*, установленный `uv`.
Команда запуска сервера:
```bash
uv run uvicorn src.main:app --reload --host 127.0.0.1 --port 8000
```
Адрес приложения: http://127.0.0.1:8000/

## Настройка переменных окружения
Для конфигурации бэкенда используется файл .env в корне проекта.

Скопируйте шаблон переменных окружения:

```Bash
cp example.env .env
```
Убедитесь, что файл .env добавлен в .gitignore и не попадет в репозиторий.

Описание переменных
```
DeepSeek / VseGPT:

DEEPSEEK_API_KEY — Обязательно. API-ключ от сервиса VseGPT (формата sk-or-vv-...).
DEEPSEEK_BASE_URL — базовый URL шлюза VseGPT (по умолчанию: https://api.vsegpt.ru/v1).
DEEPSEEK_MODEL — идентификатор модели (по умолчанию: deepseek-chat).
DEEPSEEK_TIMEOUT — таймаут ожидания ответа от нейросети в секундах.

Unsplash:
UNSPLASH_CLIENT_ID — Access Key для Unsplash API.
UNSPLASH_MAX_CONNECTIONS — максимальное количество одновременных подключений.
UNSPLASH_TIMEOUT — таймаут ожидания ответа Unsplash в секундах.
```
Групповые настройки подключения к S3 (MinIO):
Все переменные для S3 объединены в общую группу с префиксом S3__ (двойное подчеркивание):
```
S3__ENDPOINT_URL — сетевой адрес API MinIO (по умолчанию: http://localhost:9000).
S3__ACCESS_KEY — Обязательно. Логин администратора MinIO (MINIO_ROOT_USER).
S3__SECRET_KEY — Обязательно. Пароль администратора MinIO (MINIO_ROOT_PASSWORD).
S3__BUCKET_NAME — имя бакета для хранения сайтов (по умолчанию: sites).
S3__CONNECT_TIMEOUT — таймаут подключения к S3 в секундах (положительное число, по умолчанию: 5).
S3__READ_TIMEOUT — таймаут чтения данных из S3 в секундах (положительное число, по умолчанию: 10).
S3__MAX_CONNECTIONS — максимальный лимит одновременных подключений (положительное число, по умолчанию: 10).
```
Пример готового файла .env:
```
DEBUG=True

DEEPSEEK_API_KEY=sk-or-vv-1234567890abcdef
DEEPSEEK_BASE_URL=[https://api.deepseek.com/v1](https://api.deepseek.com/v1)
DEEPSEEK_MODEL=deepseek-chat

UNSPLASH_API_KEY=your_unsplash_access_key
UNSPLASH_TIMEOUT=20.0

S3__ENDPOINT_URL=http://localhost:9000
S3__ACCESS_KEY=admin
S3__SECRET_KEY=password123
S3__BUCKET_NAME=sites
S3__CONNECT_TIMEOUT=5
S3__READ_TIMEOUT=10
S3__MAX_CONNECTIONS=10
```
Проверка валидации настроек:
```Bash
uv run python -c "from src.env_settings import AppSettings; print(AppSettings().model_dump_json(indent=2))"
```
Запуск MinIO (S3-хранилище)
Скачайте бинарник MinIO для вашей ОС с официального сайта.

Запустите сервер:

```Bash
set MINIO_ROOT_USER=admin
set MINIO_ROOT_PASSWORD=password123
minio.exe server minio_data --console-address ":9001" --address ":9000"
```
Откройте веб-консоль http://localhost:9001, создайте бакет sites и сделайте его публичным (Access Policy -> Public).
