# Проверка API через curl

Выполнено: 2026-09-30T09:42:44.280976+00:00.

Использованы отдельная временная SQLite-БД, данные seed.py и случайный JWT-секрет. Основная БД не изменялась. Все приведённые ответы получены реальными HTTP-запросами curl.

Адрес при проверке: `http://127.0.0.1:65021`. В командах `$BASE_URL` обозначает адрес сервера, `$TOKEN` — токен первого запроса.

Одинаковые ошибки входа не доказывают защиту от определения аккаунта по времени ответа.

## 1. Успешный вход

```bash
curl -sS -X POST "$BASE_URL/auth/login" -H "Content-Type: application/json" --data '{"username": "alice", "password": "Al1ce-Str0ng-Pass!"}'
```

HTTP 200

```json
{
  "access_token": "<JWT скрыт; полный токен использован в следующих запросах>",
  "expires_in": 3600,
  "token_type": "Bearer"
}
```

## 2. Неверный пароль

```bash
curl -sS -X POST "$BASE_URL/auth/login" -H "Content-Type: application/json" --data '{"username": "alice", "password": "wrong"}'
```

HTTP 401

```json
{
  "error": "invalid credentials"
}
```

## 3. Неизвестный пользователь

```bash
curl -sS -X POST "$BASE_URL/auth/login" -H "Content-Type: application/json" --data '{"username": "nobody", "password": "wrong"}'
```

HTTP 401

```json
{
  "error": "invalid credentials"
}
```

## 4. SQL-инъекция в логине

```bash
curl -sS -X POST "$BASE_URL/auth/login" -H "Content-Type: application/json" --data '{"username": "\' OR \'1\'=\'1\' --", "password": "wrong"}'
```

HTTP 401

```json
{
  "error": "invalid credentials"
}
```

## 5. Отсутствуют обязательные поля

```bash
curl -sS -X POST "$BASE_URL/auth/login" -H "Content-Type: application/json" --data '{}'
```

HTTP 400

```json
{
  "error": "username and password are required"
}
```

## 6. Чтение без JWT

```bash
curl -sS -X GET "$BASE_URL/api/data"
```

HTTP 401

```json
{
  "error": "authorization header missing or malformed"
}
```

## 7. Чтение с неверным JWT

```bash
curl -sS -X GET "$BASE_URL/api/data" -H "Authorization: Bearer $TOKEN"
```

HTTP 401

```json
{
  "error": "invalid token"
}
```

## 8. Чтение с действительным JWT

```bash
curl -sS -X GET "$BASE_URL/api/data" -H "Authorization: Bearer $TOKEN"
```

HTTP 200

```json
{
  "count": 2,
  "items": [
    {
      "author": "admin",
      "body": "First post created by the seed script.",
      "created_at": "2026-09-30T09:42:43.325484",
      "id": 1,
      "title": "Welcome"
    },
    {
      "author": "alice",
      "body": "Access tokens are signed with HS256 and expire in one hour.",
      "created_at": "2026-09-30T09:42:43.325857",
      "id": 2,
      "title": "Notes on JWT"
    }
  ]
}
```

## 9. Создание поста с XSS-строкой

```bash
curl -sS -X POST "$BASE_URL/api/posts" -H "Content-Type: application/json" --data '{"title": "XSS probe", "body": "<script>alert(1)</script>"}' -H "Authorization: Bearer $TOKEN"
```

HTTP 201

```json
{
  "author": "alice",
  "body": "&lt;script&gt;alert(1)&lt;/script&gt;",
  "created_at": "2026-09-30T09:42:43.758417+00:00",
  "id": 3,
  "title": "XSS probe"
}
```

## 10. Повторное чтение экранированного поста

```bash
curl -sS -X GET "$BASE_URL/api/data" -H "Authorization: Bearer $TOKEN"
```

HTTP 200

```json
{
  "count": 3,
  "items": [
    {
      "author": "admin",
      "body": "First post created by the seed script.",
      "created_at": "2026-09-30T09:42:43.325484",
      "id": 1,
      "title": "Welcome"
    },
    {
      "author": "alice",
      "body": "Access tokens are signed with HS256 and expire in one hour.",
      "created_at": "2026-09-30T09:42:43.325857",
      "id": 2,
      "title": "Notes on JWT"
    },
    {
      "author": "alice",
      "body": "&lt;script&gt;alert(1)&lt;/script&gt;",
      "created_at": "2026-09-30T09:42:43.758417",
      "id": 3,
      "title": "XSS probe"
    }
  ]
}
```

## 11. Создание поста без JWT

```bash
curl -sS -X POST "$BASE_URL/api/posts" -H "Content-Type: application/json" --data '{"title": "Denied", "body": "Denied"}'
```

HTTP 401

```json
{
  "error": "authorization header missing or malformed"
}
```
