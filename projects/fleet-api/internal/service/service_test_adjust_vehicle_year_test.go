package service_test

import (
	"errors"
	"testing"

	"fleet-api/internal/model"
	"fleet-api/internal/service"
)

func TestAdjustVehicleYear(t *testing.T) {
	svc := seeded(t)
	before, _ := svc.GetVehicle(1)
	after, err := svc.AdjustVehicleYear(1, 2)
	if err != nil || after.Year != before.Year+2 {
		t.Fatalf("adjust = %v, %v", after.Year, err)
	}
	_, err = svc.AdjustVehicleYear(1, -(after.Year + 100))
	wantField(t, err, "year")
}

func TestAdjustVehicleMileage(t *testing.T) {
	svc := seeded(t)
	before, _ := svc.GetVehicle(1)
	after, err := svc.AdjustVehicleMileage(1, 2)
	if err != nil || after.Mileage != before.Mileage+2 {
		t.Fatalf("adjust = %v, %v", after.Mileage, err)
	}
	_, err = svc.AdjustVehicleMileage(1, -(after.Mileage + 100))
	wantField(t, err, "mileage")
}

func TestSetVehicleFuel(t *testing.T) {
	svc := seeded(t)
	last := model.VehicleFuelValues[len(model.VehicleFuelValues)-1]
	item, err := svc.SetVehicleFuel(1, last)
	if err != nil || item.Fuel != last {
		t.Fatalf("set = %v, %v", item.Fuel, err)
	}
	if got, want := svc.Vehicles.CountByFuel()[last], len(svc.Vehicles.WithFuel(last)); got != want {
		t.Fatalf("count %d != %d", got, want)
	}
}

func TestToggleVehicleActive(t *testing.T) {
	svc := seeded(t)
	before, _ := svc.GetVehicle(1)
	after, err := svc.ToggleVehicleActive(1)
	if err != nil || after.Active == before.Active {
		t.Fatalf("toggle = %v, %v", after.Active, err)
	}
}

func TestDeleteVehicle(t *testing.T) {
	svc := seeded(t)
	item, err := svc.CreateVehicle(service.SampleVehicle(14))
	if err != nil {
		t.Fatalf("create: %v", err)
	}
	if err := svc.DeleteVehicle(item.ID); err != nil {
		t.Fatalf("delete: %v", err)
	}
	if _, err := svc.GetVehicle(item.ID); !errors.Is(err, service.ErrNotFound) {
		t.Fatalf("still there: %v", err)
	}
}

func TestDeleteVehicleInUse(t *testing.T) {
	svc := seeded(t)
	if err := svc.DeleteVehicle(1); !errors.Is(err, service.ErrConflict) {
		t.Fatalf("want ErrConflict, got %v", err)
	}
}

func TestVehicleStats(t *testing.T) {
	svc := seeded(t)
	if got := svc.VehicleStats().Count; got != 3 {
		t.Fatalf("count = %d", got)
	}
}
