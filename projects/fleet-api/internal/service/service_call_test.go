package service_test

import (
	"bytes"
	"encoding/json"
	"errors"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"

	"fleet-api/internal/service"
)

func call(t *testing.T, h http.Handler, method, path string, body any) *httptest.ResponseRecorder {
	t.Helper()
	var reader *bytes.Reader
	if body == nil {
		reader = bytes.NewReader(nil)
	} else {
		data, err := json.Marshal(body)
		if err != nil {
			t.Fatalf("marshal: %v", err)
		}
		reader = bytes.NewReader(data)
	}
	rec := httptest.NewRecorder()
	h.ServeHTTP(rec, httptest.NewRequest(method, path, reader))
	return rec
}

// keep the imports used even for domains without text fields
var _ = strings.ToUpper

func TestVehicleCreateAndGet(t *testing.T) {
	svc := seeded(t)
	created, err := svc.CreateVehicle(service.SampleVehicle(10))
	if err != nil {
		t.Fatalf("create: %v", err)
	}
	got, err := svc.GetVehicle(created.ID)
	if err != nil || got != created {
		t.Fatalf("get = %+v, %v; want %+v", got, err, created)
	}
	if n := len(svc.ListVehicles()); n != 4 {
		t.Fatalf("list has %d records, want 4", n)
	}
}

func TestVehicleMissing(t *testing.T) {
	svc := seeded(t)
	if _, err := svc.GetVehicle(9999); !errors.Is(err, service.ErrNotFound) {
		t.Fatalf("want ErrNotFound, got %v", err)
	}
}

func TestVehicleRejectsBadPlate(t *testing.T) {
	svc := seeded(t)
	item := service.SampleVehicle(12)
	item.Plate = ""
	_, err := svc.CreateVehicle(item)
	wantField(t, err, "plate")
}

func TestVehicleRejectsBadMake(t *testing.T) {
	svc := seeded(t)
	item := service.SampleVehicle(12)
	item.Make = ""
	_, err := svc.CreateVehicle(item)
	wantField(t, err, "make")
}

func TestVehicleRejectsBadModel(t *testing.T) {
	svc := seeded(t)
	item := service.SampleVehicle(12)
	item.Model = ""
	_, err := svc.CreateVehicle(item)
	wantField(t, err, "model")
}
