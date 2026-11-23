package service_test

import (
	"encoding/json"
	"errors"
	"fmt"
	"net/http"
	"strings"
	"testing"

	"warehouse-api/internal/httpapi"
	"warehouse-api/internal/model"
	"warehouse-api/internal/service"
)

func TestSearchStockMovementReference(t *testing.T) {
	svc := seeded(t)
	target, _ := svc.GetStockMovement(2)
	for _, item := range svc.StockMovements.SearchReference(strings.ToUpper(target.Reference)) {
		if item.ID == target.ID {
			return
		}
	}
	t.Fatalf("search did not find %q", target.Reference)
}

func TestDeleteStockMovement(t *testing.T) {
	svc := seeded(t)
	item, err := svc.CreateStockMovement(service.SampleStockMovement(14))
	if err != nil {
		t.Fatalf("create: %v", err)
	}
	if err := svc.DeleteStockMovement(item.ID); err != nil {
		t.Fatalf("delete: %v", err)
	}
	if _, err := svc.GetStockMovement(item.ID); !errors.Is(err, service.ErrNotFound) {
		t.Fatalf("still there: %v", err)
	}
}

func TestStockMovementStats(t *testing.T) {
	svc := seeded(t)
	if got := svc.StockMovementStats().Count; got != 3 {
		t.Fatalf("count = %d", got)
	}
}

func TestStockMovementAPI(t *testing.T) {
	h := httpapi.New(seeded(t))
	rec := call(t, h, http.MethodPost, "/stock-movements", service.SampleStockMovement(15))
	if rec.Code != http.StatusCreated {
		t.Fatalf("POST = %d %s", rec.Code, rec.Body)
	}
	var created model.StockMovement
	if err := json.Unmarshal(rec.Body.Bytes(), &created); err != nil {
		t.Fatalf("decode: %v", err)
	}
	path := fmt.Sprintf("/stock-movements/%d", created.ID)
	if rec := call(t, h, http.MethodGet, path, nil); rec.Code != http.StatusOK {
		t.Fatalf("GET = %d", rec.Code)
	}
	if rec := call(t, h, http.MethodGet, "/stock-movements?size=2&page=1", nil); rec.Code != http.StatusOK {
		t.Fatalf("list = %d", rec.Code)
	}
	if rec := call(t, h, http.MethodGet, "/stock-movements/stats", nil); rec.Code != http.StatusOK {
		t.Fatalf("stats = %d", rec.Code)
	}
	if rec := call(t, h, http.MethodPost, "/stock-movements", map[string]int{"no_such_field": 1}); rec.Code != http.StatusBadRequest {
		t.Fatalf("bad POST = %d", rec.Code)
	}
	if rec := call(t, h, http.MethodDelete, path, nil); rec.Code != http.StatusNoContent {
		t.Fatalf("DELETE = %d", rec.Code)
	}
	if rec := call(t, h, http.MethodGet, path, nil); rec.Code != http.StatusNotFound {
		t.Fatalf("GET after delete = %d", rec.Code)
	}
}
