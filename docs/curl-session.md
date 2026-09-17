# Manual verification with curl

Server started with `python wsgi.py` on http://127.0.0.1:5000, database seeded by `python seed.py`.
JWT values are truncated below for readability.

### 1. Successful login

HTTP 200

```json
{"access_token":"eyJhbGciOiJIUzI1NiIsInR5cCI6Ik...truncated...","expires_in":3600,"token_type":"Bearer"}
```

### 2. Login with a wrong password

HTTP 401

```json
{"error":"invalid credentials"}
```

### 3. Login as a user that does not exist, identical to case 2 so accounts cannot be enumerated

HTTP 401

```json
{"error":"invalid credentials"}
```

### 4. SQL injection payload in the username field

HTTP 401

```json
{"error":"invalid credentials"}
```

### 5. Login without a request body

HTTP 400

```json
{"error":"username and password are required"}
```

### 6. GET /api/data without a token

HTTP 401

```json
{"error":"authorization header missing or malformed"}
```

### 7. GET /api/data with a forged token

HTTP 401

```json
{"error":"invalid token"}
```

### 8. GET /api/data with a valid token

HTTP 200

```json
{"count":2,"items":[{"author":"admin","body":"First post created by the seed script.","created_at":"2026-09-17T10:59:45.035358","id":1,"title":"Welcome"},{"author":"alice","body":"Access tokens are signed with HS256 and expire in one hour.","created_at":"2026-09-17T10:59:45.035972","id":2,"title":"Notes on JWT"}]}
```

### 9. POST /api/posts with an XSS payload

HTTP 201

```json
{"author":"alice","body":"&lt;script&gt;alert(1)&lt;/script&gt;","created_at":"2026-09-17T11:00:28.184813+00:00","id":3,"title":"XSS probe"}
```

### 10. GET /api/data returns the stored payload escaped

HTTP 200

```json
{"count":3,"items":[{"author":"admin","body":"First post created by the seed script.","created_at":"2026-09-17T10:59:45.035358","id":1,"title":"Welcome"},{"author":"alice","body":"Access tokens are signed with HS256 and expire in one hour.","created_at":"2026-09-17T10:59:45.035972","id":2,"title":"Notes on JWT"},{"author":"alice","body":"&lt;script&gt;alert(1)&lt;/script&gt;","created_at":"2026-09-17T11:00:28.184813","id":3,"title":"XSS probe"}]}
```

### 11. POST /api/posts without a token

HTTP 401

```json
{"error":"authorization header missing or malformed"}
```

