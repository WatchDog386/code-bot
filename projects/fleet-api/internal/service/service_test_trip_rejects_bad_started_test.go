package service_test

import (
	"errors"
	"testing"

	"fleet-api/internal/service"
)

func TestTripRejectsBadStarted(t *testing.T) {
	svc := seeded(t)
	item := service.SampleTrip(12)
	item.Started = "2026-02-30"
	_, err := svc.CreateTrip(item)
	wantField(t, err, "started")
}

func TestTripRejectsBadDistanceKm(t *testing.T) {
	svc := seeded(t)
	item := service.SampleTrip(12)
	item.DistanceKm = -1
	_, err := svc.CreateTrip(item)
	wantField(t, err, "distance_km")
}

func TestTripRejectsBadPurpose(t *testing.T) {
	svc := seeded(t)
	item := service.SampleTrip(12)
	item.Purpose = ""
	_, err := svc.CreateTrip(item)
	wantField(t, err, "purpose")
}

func TestTripRejectsBadStatus(t *testing.T) {
	svc := seeded(t)
	item := service.SampleTrip(12)
	item.Status = "nope"
	_, err := svc.CreateTrip(item)
	wantField(t, err, "status")
}

func TestTripVehicleIDMustExist(t *testing.T) {
	svc := seeded(t)
	item := service.SampleTrip(13)
	item.VehicleID = 9999
	if _, err := svc.CreateTrip(item); !errors.Is(err, service.ErrNotFound) {
		t.Fatalf("want ErrNotFound, got %v", err)
	}
}

func TestTripDriverIDMustExist(t *testing.T) {
	svc := seeded(t)
	item := service.SampleTrip(13)
	item.DriverID = 9999
	if _, err := svc.CreateTrip(item); !errors.Is(err, service.ErrNotFound) {
		t.Fatalf("want ErrNotFound, got %v", err)
	}
}

func TestTripStartedRanges(t *testing.T) {
	svc := seeded(t)
	day := service.SampleTrip(2).Started
	total := len(svc.Trips.StartedBefore(day)) + len(svc.Trips.StartedOn(day)) + len(svc.Trips.StartedAfter(day))
	if total != svc.Trips.Count() {
		t.Fatalf("ranges cover %d of %d records", total, svc.Trips.Count())
	}
}

func TestAdjustTripDistanceKm(t *testing.T) {
	svc := seeded(t)
	before, _ := svc.GetTrip(1)
	after, err := svc.AdjustTripDistanceKm(1, 1.5)
	if err != nil || after.DistanceKm-before.DistanceKm < 1.49 || after.DistanceKm-before.DistanceKm > 1.51 {
		t.Fatalf("adjust = %v, %v", after.DistanceKm, err)
	}
}
