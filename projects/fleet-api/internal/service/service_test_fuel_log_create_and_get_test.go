package service_test

import (
	"errors"
	"testing"

	"fleet-api/internal/service"
)

func TestFuelLogCreateAndGet(t *testing.T) {
	svc := seeded(t)
	created, err := svc.CreateFuelLog(service.SampleFuelLog(10))
	if err != nil {
		t.Fatalf("create: %v", err)
	}
	got, err := svc.GetFuelLog(created.ID)
	if err != nil || got != created {
		t.Fatalf("get = %+v, %v; want %+v", got, err, created)
	}
	if n := len(svc.ListFuelLogs()); n != 4 {
		t.Fatalf("list has %d records, want 4", n)
	}
}

func TestFuelLogMissing(t *testing.T) {
	svc := seeded(t)
	if _, err := svc.GetFuelLog(9999); !errors.Is(err, service.ErrNotFound) {
		t.Fatalf("want ErrNotFound, got %v", err)
	}
}

func TestFuelLogRejectsBadVehicleID(t *testing.T) {
	svc := seeded(t)
	item := service.SampleFuelLog(12)
	item.VehicleID = 0
	_, err := svc.CreateFuelLog(item)
	wantField(t, err, "vehicle_id")
}

func TestFuelLogRejectsBadFilled(t *testing.T) {
	svc := seeded(t)
	item := service.SampleFuelLog(12)
	item.Filled = "2026-02-30"
	_, err := svc.CreateFuelLog(item)
	wantField(t, err, "filled")
}
