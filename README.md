# Chipollino web

### Инструкция запуска:
В репозитории есть Nix-окружение (`shell.nix`) и сборка Docker-образа (`docker.nix`).

Для разработки:
- `nix-shell`
- `python manage.py migrate`
- `python manage.py runserver`

Для сборки Docker-образов:
- `nix-build docker.nix`
- `docker load < result/app`
- `docker load < result/caddy`

Запуск через compose с собранными образами:
`docker compose up -d`
