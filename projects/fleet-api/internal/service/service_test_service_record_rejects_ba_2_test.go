package service_test

import (
	"errors"
	"strings"
	"testing"

	"fleet-api/internal/service"
)

func TestServiceRecordRejectsBadKind(t *testing.T) {
	svc := seeded(t)
	item := service.SampleServiceRecord(12)
	item.Kind = "nope"
	_, err := svc.CreateServiceRecord(item)
	wantField(t, err, "kind")
}

func TestServiceRecordRejectsBadNotes(t *testing.T) {
	svc := seeded(t)
	item := service.SampleServiceRecord(12)
	item.Notes = strings.Repeat("x", 3000)
	_, err := svc.CreateServiceRecord(item)
	wantField(t, err, "notes")
}

func TestServiceRecordVehicleIDMustExist(t *testing.T) {
	svc := seeded(t)
	item := service.SampleServiceRecord(13)
	item.VehicleID = 9999
	if _, err := svc.CreateServiceRecord(item); !errors.Is(err, service.ErrNotFound) {
		t.Fatalf("want ErrNotFound, got %v", err)
	}
}
