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

func TestProductAPI(t *testing.T) {
	h := httpapi.New(seeded(t))
	rec := call(t, h, http.MethodPost, "/products", service.SampleProduct(15))
	if rec.Code != http.StatusCreated {
		t.Fatalf("POST = %d %s", rec.Code, rec.Body)
	}
	var created model.Product
	if err := json.Unmarshal(rec.Body.Bytes(), &created); err != nil {
		t.Fatalf("decode: %v", err)
	}
	path := fmt.Sprintf("/products/%d", created.ID)
	if rec := call(t, h, http.MethodGet, path, nil); rec.Code != http.StatusOK {
		t.Fatalf("GET = %d", rec.Code)
	}
	if rec := call(t, h, http.MethodGet, "/products?size=2&page=1", nil); rec.Code != http.StatusOK {
		t.Fatalf("list = %d", rec.Code)
	}
	if rec := call(t, h, http.MethodGet, "/products/stats", nil); rec.Code != http.StatusOK {
		t.Fatalf("stats = %d", rec.Code)
	}
	if rec := call(t, h, http.MethodPost, "/products", map[string]int{"no_such_field": 1}); rec.Code != http.StatusBadRequest {
		t.Fatalf("bad POST = %d", rec.Code)
	}
	if rec := call(t, h, http.MethodDelete, path, nil); rec.Code != http.StatusNoContent {
		t.Fatalf("DELETE = %d", rec.Code)
	}
	if rec := call(t, h, http.MethodGet, path, nil); rec.Code != http.StatusNotFound {
		t.Fatalf("GET after delete = %d", rec.Code)
	}
}

func TestBinCreateAndGet(t *testing.T) {
	svc := seeded(t)
	created, err := svc.CreateBin(service.SampleBin(10))
	if err != nil {
		t.Fatalf("create: %v", err)
	}
	got, err := svc.GetBin(created.ID)
	if err != nil || got != created {
		t.Fatalf("get = %+v, %v; want %+v", got, err, created)
	}
	if n := len(svc.ListBins()); n != 4 {
		t.Fatalf("list has %d records, want 4", n)
	}
}

func TestBinMissing(t *testing.T) {
	svc := seeded(t)
	if _, err := svc.GetBin(9999); !errors.Is(err, service.ErrNotFound) {
		t.Fatalf("want ErrNotFound, got %v", err)
	}
}

func TestBinRejectsBadCode(t *testing.T) {
	svc := seeded(t)
	item := service.SampleBin(12)
	item.Code = ""
	_, err := svc.CreateBin(item)
	wantField(t, err, "code")
}

func TestBinRejectsBadAisle(t *testing.T) {
	svc := seeded(t)
	item := service.SampleBin(12)
	item.Aisle = ""
	_, err := svc.CreateBin(item)
	wantField(t, err, "aisle")
}

func TestBinRejectsBadShelf(t *testing.T) {
	svc := seeded(t)
	item := service.SampleBin(12)
	item.Shelf = -1
	_, err := svc.CreateBin(item)
	wantField(t, err, "shelf")
}
