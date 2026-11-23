package service_test

import (
	"testing"

	"fleet-api/internal/service"
)

func TestServiceRecordRejectsBadServiced(t *testing.T) {
	svc := seeded(t)
	item := service.SampleServiceRecord(12)
	item.Serviced = "2026-02-30"
	_, err := svc.CreateServiceRecord(item)
	wantField(t, err, "serviced")
}

func TestServiceRecordRejectsBadOdometer(t *testing.T) {
	svc := seeded(t)
	item := service.SampleServiceRecord(12)
	item.Odometer = -1
	_, err := svc.CreateServiceRecord(item)
	wantField(t, err, "odometer")
}

func TestServiceRecordRejectsBadCost(t *testing.T) {
	svc := seeded(t)
	item := service.SampleServiceRecord(12)
	item.Cost = -5
	_, err := svc.CreateServiceRecord(item)
	wantField(t, err, "cost")
}
