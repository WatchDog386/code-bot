# Warehouse Inventory API

The JSON API listens on `http://127.0.0.1:8080` by default. Check `GET /health` before use.
Collections include suppliers, products, bins, stock movements, purchase orders, and documents.
Each collection provides list, create, read, update, delete, and statistics routes. Lists accept
`q`, `page`, and `size` query parameters.

```sh
curl http://127.0.0.1:8080/products?page=1\&size=20
curl -X POST http://127.0.0.1:8080/products -H "Content-Type: application/json" \
  -d '{"supplier_id":1,"sku":"TOOL-001","name":"Adjustable wrench","unit_cost":8.50,"unit_price":14.00,"reorder_level":6,"category":"tools","active":true}'
```

The server adds an `X-Request-ID` response header for support logs. Configure the listener and
startup demo records with `WAREHOUSE_HOST`, `WAREHOUSE_PORT`, and `WAREHOUSE_SEED_SIZE`.
