# Fleet Management API

The JSON API listens on `http://127.0.0.1:8080` by default. Check `GET /health` before use.
Collections include vehicles, drivers, trips, fuel logs, service records, incidents, documents,
and notifications. Each collection provides list, create, read, update, delete, and statistics
routes. Lists accept `q`, `page`, and `size` query parameters.

```sh
curl http://127.0.0.1:8080/vehicles?page=1\&size=20
curl -X POST http://127.0.0.1:8080/vehicles -H "Content-Type: application/json" \
  -d '{"plate":"KAA-123A","make":"Toyota","model":"Corolla","year":2022,"mileage":25000,"fuel":"petrol","active":true}'
```

The server adds an `X-Request-ID` response header for support logs. Configure the listener and
startup demo records with `FLEET_HOST`, `FLEET_PORT`, and `FLEET_SEED_SIZE`.
