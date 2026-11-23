package service_test

import (
	"encoding/json"
	"errors"
	"fmt"
	"net/http"
	"testing"

	"fleet-api/internal/httpapi"
	"fleet-api/internal/model"
	"fleet-api/internal/service"
)

func TestVehicleAPI(t *testing.T) {
	h := httpapi.New(seeded(t))
	rec := call(t, h, http.MethodPost, "/vehicles", service.SampleVehicle(15))
	if rec.Code != http.StatusCreated {
		t.Fatalf("POST = %d %s", rec.Code, rec.Body)
	}
	var created model.Vehicle
	if err := json.Unmarshal(rec.Body.Bytes(), &created); err != nil {
		t.Fatalf("decode: %v", err)
	}
	path := fmt.Sprintf("/vehicles/%d", created.ID)
	if rec := call(t, h, http.MethodGet, path, nil); rec.Code != http.StatusOK {
		t.Fatalf("GET = %d", rec.Code)
	}
	if rec := call(t, h, http.MethodGet, "/vehicles?size=2&page=1", nil); rec.Code != http.StatusOK {
		t.Fatalf("list = %d", rec.Code)
	}
	if rec := call(t, h, http.MethodGet, "/vehicles/stats", nil); rec.Code != http.StatusOK {
		t.Fatalf("stats = %d", rec.Code)
	}
	if rec := call(t, h, http.MethodPost, "/vehicles", map[string]int{"no_such_field": 1}); rec.Code != http.StatusBadRequest {
		t.Fatalf("bad POST = %d", rec.Code)
	}
	if rec := call(t, h, http.MethodDelete, path, nil); rec.Code != http.StatusNoContent {
		t.Fatalf("DELETE = %d", rec.Code)
	}
	if rec := call(t, h, http.MethodGet, path, nil); rec.Code != http.StatusNotFound {
		t.Fatalf("GET after delete = %d", rec.Code)
	}
}

func TestDriverCreateAndGet(t *testing.T) {
	svc := seeded(t)
	created, err := svc.CreateDriver(service.SampleDriver(10))
	if err != nil {
		t.Fatalf("create: %v", err)
	}
	got, err := svc.GetDriver(created.ID)
	if err != nil || got != created {
		t.Fatalf("get = %+v, %v; want %+v", got, err, created)
	}
	if n := len(svc.ListDrivers()); n != 4 {
		t.Fatalf("list has %d records, want 4", n)
	}
}

func TestDriverMissing(t *testing.T) {
	svc := seeded(t)
	if _, err := svc.GetDriver(9999); !errors.Is(err, service.ErrNotFound) {
		t.Fatalf("want ErrNotFound, got %v", err)
	}
}
