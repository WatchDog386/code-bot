# link-shortener

A tiny URL shortener written in Go using only the standard library.

## Endpoints

| Method | Path         | Description              |
|--------|--------------|--------------------------|
| POST   | /api/links   | Create a short link      |
| GET    | /{code}      | Redirect to the target   |
| GET    | /healthz     | Liveness probe           |

## Example

```bash
curl -X POST localhost:8080/api/links -d '{"url": "https://go.dev", "ttl_minutes": 60}'
```

## Development

```bash
go test ./...
go run ./cmd/server
```
