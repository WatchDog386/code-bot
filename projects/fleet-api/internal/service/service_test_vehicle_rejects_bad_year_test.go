package service_test

import (
	"strings"
	"testing"

	"fleet-api/internal/service"
)

func TestVehicleRejectsBadYear(t *testing.T) {
	svc := seeded(t)
	item := service.SampleVehicle(12)
	item.Year = -1
	_, err := svc.CreateVehicle(item)
	wantField(t, err, "year")
}

func TestVehicleRejectsBadMileage(t *testing.T) {
	svc := seeded(t)
	item := service.SampleVehicle(12)
	item.Mileage = -1
	_, err := svc.CreateVehicle(item)
	wantField(t, err, "mileage")
}

func TestVehicleRejectsBadFuel(t *testing.T) {
	svc := seeded(t)
	item := service.SampleVehicle(12)
	item.Fuel = "nope"
	_, err := svc.CreateVehicle(item)
	wantField(t, err, "fuel")
}

func TestSearchVehiclePlate(t *testing.T) {
	svc := seeded(t)
	target, _ := svc.GetVehicle(2)
	for _, item := range svc.Vehicles.SearchPlate(strings.ToUpper(target.Plate)) {
		if item.ID == target.ID {
			return
		}
	}
	t.Fatalf("search did not find %q", target.Plate)
}

func TestSearchVehicleMake(t *testing.T) {
	svc := seeded(t)
	target, _ := svc.GetVehicle(2)
	for _, item := range svc.Vehicles.SearchMake(strings.ToUpper(target.Make)) {
		if item.ID == target.ID {
			return
		}
	}
	t.Fatalf("search did not find %q", target.Make)
}

func TestSearchVehicleModel(t *testing.T) {
	svc := seeded(t)
	target, _ := svc.GetVehicle(2)
	for _, item := range svc.Vehicles.SearchModel(strings.ToUpper(target.Model)) {
		if item.ID == target.ID {
			return
		}
	}
	t.Fatalf("search did not find %q", target.Model)
}
