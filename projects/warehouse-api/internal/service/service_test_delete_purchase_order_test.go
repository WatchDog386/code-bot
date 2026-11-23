package service_test

import (
	"encoding/json"
	"errors"
	"fmt"
	"net/http"
	"testing"

	"warehouse-api/internal/httpapi"
	"warehouse-api/internal/model"
	"warehouse-api/internal/service"
)

func TestDeletePurchaseOrder(t *testing.T) {
	svc := seeded(t)
	item, err := svc.CreatePurchaseOrder(service.SamplePurchaseOrder(14))
	if err != nil {
		t.Fatalf("create: %v", err)
	}
	if err := svc.DeletePurchaseOrder(item.ID); err != nil {
		t.Fatalf("delete: %v", err)
	}
	if _, err := svc.GetPurchaseOrder(item.ID); !errors.Is(err, service.ErrNotFound) {
		t.Fatalf("still there: %v", err)
	}
}

func TestPurchaseOrderStats(t *testing.T) {
	svc := seeded(t)
	if got := svc.PurchaseOrderStats().Count; got != 3 {
		t.Fatalf("count = %d", got)
	}
}

func TestPurchaseOrderAPI(t *testing.T) {
	h := httpapi.New(seeded(t))
	rec := call(t, h, http.MethodPost, "/purchase-orders", service.SamplePurchaseOrder(15))
	if rec.Code != http.StatusCreated {
		t.Fatalf("POST = %d %s", rec.Code, rec.Body)
	}
	var created model.PurchaseOrder
	if err := json.Unmarshal(rec.Body.Bytes(), &created); err != nil {
		t.Fatalf("decode: %v", err)
	}
	path := fmt.Sprintf("/purchase-orders/%d", created.ID)
	if rec := call(t, h, http.MethodGet, path, nil); rec.Code != http.StatusOK {
		t.Fatalf("GET = %d", rec.Code)
	}
	if rec := call(t, h, http.MethodGet, "/purchase-orders?size=2&page=1", nil); rec.Code != http.StatusOK {
		t.Fatalf("list = %d", rec.Code)
	}
	if rec := call(t, h, http.MethodGet, "/purchase-orders/stats", nil); rec.Code != http.StatusOK {
		t.Fatalf("stats = %d", rec.Code)
	}
	if rec := call(t, h, http.MethodPost, "/purchase-orders", map[string]int{"no_such_field": 1}); rec.Code != http.StatusBadRequest {
		t.Fatalf("bad POST = %d", rec.Code)
	}
	if rec := call(t, h, http.MethodDelete, path, nil); rec.Code != http.StatusNoContent {
		t.Fatalf("DELETE = %d", rec.Code)
	}
	if rec := call(t, h, http.MethodGet, path, nil); rec.Code != http.StatusNotFound {
		t.Fatalf("GET after delete = %d", rec.Code)
	}
}

func TestStockCountCreateAndGet(t *testing.T) {
	svc := seeded(t)
	created, err := svc.CreateStockCount(service.SampleStockCount(10))
	if err != nil {
		t.Fatalf("create: %v", err)
	}
	got, err := svc.GetStockCount(created.ID)
	if err != nil || got != created {
		t.Fatalf("get = %+v, %v; want %+v", got, err, created)
	}
	if n := len(svc.ListStockCounts()); n != 4 {
		t.Fatalf("list has %d records, want 4", n)
	}
}
