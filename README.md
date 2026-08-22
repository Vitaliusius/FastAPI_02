# FastAI

## Репозиторий для бэкенд-разработчиков.

Инструкции и справочная информация по разворачиванию локальной инсталляции собраны
в документе [CONTRIBUTING.md](./CONTRIBUTING.md).

Требования к окружению (версия Python 3.13.*, установленный uv).
Команда запуска сервера: 
```fastapi dev src/main.py.```
Адрес приложения: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
## Настройка переменных окружения

1. Скопируйте шаблон переменных окружения:
```bash
   cp example.env .env
```
2. Убедитесь, что файл .env добавлен в .gitignore и не попадет в репозиторий.

3. Заполните обязательные переменные в .env:
```
DEEPSEEK_API_KEY — API-ключ от сервиса VseGPT (формата sk-or-vv-...). Получить можно в личном кабинете VseGPT.

DEEPSEEK_BASE_URL — базовый URL шлюза VseGPT: https://api.vsegpt.ru/v1.

DEEPSEEK_MODEL — идентификатор модели в VseGPT (например, deepseek/deepseek-chat или openai/gpt-4o-mini).

UNSPLASH_API_KEY — Access Key для Unsplash API. Получить можно на [Unsplash Developers](https://unsplash.com/).
```
4. Проверьте валидацию настроек:

```bash
uv run python src/env_settings.py
```