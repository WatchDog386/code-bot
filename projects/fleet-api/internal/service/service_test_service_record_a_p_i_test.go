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

func TestServiceRecordAPI(t *testing.T) {
	h := httpapi.New(seeded(t))
	rec := call(t, h, http.MethodPost, "/service-records", service.SampleServiceRecord(15))
	if rec.Code != http.StatusCreated {
		t.Fatalf("POST = %d %s", rec.Code, rec.Body)
	}
	var created model.ServiceRecord
	if err := json.Unmarshal(rec.Body.Bytes(), &created); err != nil {
		t.Fatalf("decode: %v", err)
	}
	path := fmt.Sprintf("/service-records/%d", created.ID)
	if rec := call(t, h, http.MethodGet, path, nil); rec.Code != http.StatusOK {
		t.Fatalf("GET = %d", rec.Code)
	}
	if rec := call(t, h, http.MethodGet, "/service-records?size=2&page=1", nil); rec.Code != http.StatusOK {
		t.Fatalf("list = %d", rec.Code)
	}
	if rec := call(t, h, http.MethodGet, "/service-records/stats", nil); rec.Code != http.StatusOK {
		t.Fatalf("stats = %d", rec.Code)
	}
	if rec := call(t, h, http.MethodPost, "/service-records", map[string]int{"no_such_field": 1}); rec.Code != http.StatusBadRequest {
		t.Fatalf("bad POST = %d", rec.Code)
	}
	if rec := call(t, h, http.MethodDelete, path, nil); rec.Code != http.StatusNoContent {
		t.Fatalf("DELETE = %d", rec.Code)
	}
	if rec := call(t, h, http.MethodGet, path, nil); rec.Code != http.StatusNotFound {
		t.Fatalf("GET after delete = %d", rec.Code)
	}
}

func TestIncidentCreateAndGet(t *testing.T) {
	svc := seeded(t)
	created, err := svc.CreateIncident(service.SampleIncident(10))
	if err != nil {
		t.Fatalf("create: %v", err)
	}
	got, err := svc.GetIncident(created.ID)
	if err != nil || got != created {
		t.Fatalf("get = %+v, %v; want %+v", got, err, created)
	}
	if n := len(svc.ListIncidents()); n != 4 {
		t.Fatalf("list has %d records, want 4", n)
	}
}

func TestIncidentMissing(t *testing.T) {
	svc := seeded(t)
	if _, err := svc.GetIncident(9999); !errors.Is(err, service.ErrNotFound) {
		t.Fatalf("want ErrNotFound, got %v", err)
	}
}

func TestIncidentRejectsBadVehicleID(t *testing.T) {
	svc := seeded(t)
	item := service.SampleIncident(12)
	item.VehicleID = 0
	_, err := svc.CreateIncident(item)
	wantField(t, err, "vehicle_id")
}

func TestIncidentRejectsBadDriverID(t *testing.T) {
	svc := seeded(t)
	item := service.SampleIncident(12)
	item.DriverID = 0
	_, err := svc.CreateIncident(item)
	wantField(t, err, "driver_id")
}
