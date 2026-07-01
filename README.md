# Chipollino web

### Инструкция запуска:
В репозитории используется [devenv](https://devenv.sh): окружение для разработки и сборка Docker-образов описаны в `devenv.nix`, а все внешние зависимости закреплены в `devenv.yaml`.

Для разработки:
- `devenv shell`
- `python manage.py migrate`
- `python manage.py runserver`

Или одной командой через process-compose:
- `devenv up`

Для сборки Docker-образов:
- `devenv container build app`
- `devenv container copy app`
- `devenv container build caddy`
- `devenv container copy caddy`

Запуск через compose с собранными образами:
`docker compose up -d`
