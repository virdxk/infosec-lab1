# Проверка API через curl

Сервер запущен локально (`python wsgi.py`) на чистой базе после `python seed.py`. Токен из шага 1 сохранён в `$TOKEN` и в ответах заменён на `<JWT>`.

```bash
BASE_URL=http://127.0.0.1:5000
```

## 1. Вход

```bash
curl -s -X POST "$BASE_URL/auth/login" \
  -H 'Content-Type: application/json' \
  -d '{"username": "alice", "password": "Al1ce-Str0ng-Pass!"}'
```

HTTP 200

```json
{
  "access_token": "<JWT>"
}
```

## 2. Неверный пароль

```bash
curl -s -X POST "$BASE_URL/auth/login" \
  -H 'Content-Type: application/json' \
  -d '{"username": "alice", "password": "wrong"}'
```

HTTP 401

```json
{
  "error": "invalid credentials"
}
```

## 3. SQL-инъекция в логине

```bash
curl -s -X POST "$BASE_URL/auth/login" \
  -H 'Content-Type: application/json' \
  -d "{\"username\": \"' OR 1=1 --\", \"password\": \"x\"}"
```

HTTP 401

```json
{
  "error": "invalid credentials"
}
```

## 4. Данные без токена

```bash
curl -s "$BASE_URL/api/data"
```

HTTP 401

```json
{
  "error": "missing token"
}
```

## 5. Токен без подписи (alg: none)

```bash
curl -s "$BASE_URL/api/data" \
  -H 'Authorization: Bearer eyJhbGciOiJub25lIn0.eyJzdWIiOiIxIn0.'
```

HTTP 401

```json
{
  "error": "invalid token"
}
```

## 6. Данные с токеном

```bash
curl -s "$BASE_URL/api/data" -H "Authorization: Bearer $TOKEN"
```

HTTP 200

```json
[
  {
    "author": "alice",
    "body": "First post.",
    "id": 1,
    "title": "Welcome"
  },
  {
    "author": "bob",
    "body": "Tokens expire in one hour.",
    "id": 2,
    "title": "Notes on JWT"
  }
]
```

## 7. Создание поста

```bash
curl -s -X POST "$BASE_URL/api/posts" \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"title": "Hello", "body": "World"}'
```

HTTP 201

```json
{
  "author": "alice",
  "body": "World",
  "id": 3,
  "title": "Hello"
}
```

## 8. XSS в посте

```bash
curl -s -X POST "$BASE_URL/api/posts" \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"title": "XSS", "body": "<script>alert(1)</script>"}'
```

HTTP 201

```json
{
  "author": "alice",
  "body": "&lt;script&gt;alert(1)&lt;/script&gt;",
  "id": 4,
  "title": "XSS"
}
```

## 9. Пост без обязательных полей

```bash
curl -s -X POST "$BASE_URL/api/posts" \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"title": "only title"}'
```

HTTP 400

```json
{
  "error": "title and body are required"
}
```
