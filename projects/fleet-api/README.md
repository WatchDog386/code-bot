# fleet-api

Fleet Management service in Go (standard library only).

Records: Vehicle, Driver, Trip, FuelLog, ServiceRecord, Incident, Document, Notification.

```bash
go test ./...
go run ./cmd/server     # http://127.0.0.1:8080/health
go run ./examples/sample
```

The project includes environment validated startup settings, request ID and panic recovery
middleware, container support, and endpoint notes in `docs/API.md`. Set `FLEET_HOST`, `FLEET_PORT`,
and `FLEET_SEED_SIZE` to configure the server.
