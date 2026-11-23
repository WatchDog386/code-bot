package service_test

import (
	"errors"
	"testing"

	"fleet-api/internal/service"
)

func TestDeleteFuelLog(t *testing.T) {
	svc := seeded(t)
	item, err := svc.CreateFuelLog(service.SampleFuelLog(14))
	if err != nil {
		t.Fatalf("create: %v", err)
	}
	if err := svc.DeleteFuelLog(item.ID); err != nil {
		t.Fatalf("delete: %v", err)
	}
	if _, err := svc.GetFuelLog(item.ID); !errors.Is(err, service.ErrNotFound) {
		t.Fatalf("still there: %v", err)
	}
}

func TestFuelLogStats(t *testing.T) {
	svc := seeded(t)
	if got := svc.FuelLogStats().Count; got != 3 {
		t.Fatalf("count = %d", got)
	}
}
