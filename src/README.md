# Запуск

```bash
docker compose up -d

python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# При необходимости:
export DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/tracker

alembic upgrade head
uvicorn app.main:app --reload
```

Swagger:

- http://127.0.0.1:8000/docs

## Пример создания пользователя

```bash
curl -X POST http://127.0.0.1:8000/users \
  -H 'Content-Type: application/json' \
  -d '{
    "username": "alice",
    "email": "alice@example.com",
    "hashed_password": "demo_hash"
  }'
```

> Для учебного прототипа API принимает `hashed_password` как готовое значение. Реальная аутентификация и хеширование паролей специально не реализованы.


## Пример создания задачи

```bash
curl -X POST http://127.0.0.1:8000/work-items \
  -H 'Content-Type: application/json' \
  -d '{
    "project_id": "22222222-2222-2222-2222-222222222222",
    "creator_id": "11111111-1111-1111-1111-111111111111",
    "human_id": "TASK-1",
    "title": "Сделать авторизацию",
    "description": "Реализовать вход пользователя",
    "status": "todo",
    "extrafields": {"priority": "high", "type": "backend"}
  }'
```
