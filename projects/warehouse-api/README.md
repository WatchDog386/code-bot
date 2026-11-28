# warehouse-api

Warehouse Inventory service in Go (standard library only).

Records: Supplier, Product, Bin, StockMovement, PurchaseOrder, StockCount, Document, Notification.

```bash
go test ./...
go run ./cmd/server     # http://127.0.0.1:8080/health
go run ./examples/sample
```

The project includes environment validated startup settings, request ID and panic recovery
middleware, container support, and endpoint notes in `docs/API.md`. Set `WAREHOUSE_HOST`,
`WAREHOUSE_PORT`, and `WAREHOUSE_SEED_SIZE` to configure the server.
