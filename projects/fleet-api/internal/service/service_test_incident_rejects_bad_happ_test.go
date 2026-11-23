package service_test

import (
	"errors"
	"testing"

	"fleet-api/internal/service"
)

func TestIncidentRejectsBadHappened(t *testing.T) {
	svc := seeded(t)
	item := service.SampleIncident(12)
	item.Happened = "2026-02-30"
	_, err := svc.CreateIncident(item)
	wantField(t, err, "happened")
}

func TestIncidentRejectsBadSeverity(t *testing.T) {
	svc := seeded(t)
	item := service.SampleIncident(12)
	item.Severity = "nope"
	_, err := svc.CreateIncident(item)
	wantField(t, err, "severity")
}

func TestIncidentRejectsBadDamageCost(t *testing.T) {
	svc := seeded(t)
	item := service.SampleIncident(12)
	item.DamageCost = -5
	_, err := svc.CreateIncident(item)
	wantField(t, err, "damage_cost")
}

func TestIncidentVehicleIDMustExist(t *testing.T) {
	svc := seeded(t)
	item := service.SampleIncident(13)
	item.VehicleID = 9999
	if _, err := svc.CreateIncident(item); !errors.Is(err, service.ErrNotFound) {
		t.Fatalf("want ErrNotFound, got %v", err)
	}
}

func TestIncidentDriverIDMustExist(t *testing.T) {
	svc := seeded(t)
	item := service.SampleIncident(13)
	item.DriverID = 9999
	if _, err := svc.CreateIncident(item); !errors.Is(err, service.ErrNotFound) {
		t.Fatalf("want ErrNotFound, got %v", err)
	}
}
