package service_test

import (
	"errors"
	"strings"
	"testing"

	"fleet-api/internal/model"
	"fleet-api/internal/service"
)

func TestSearchTripPurpose(t *testing.T) {
	svc := seeded(t)
	target, _ := svc.GetTrip(2)
	for _, item := range svc.Trips.SearchPurpose(strings.ToUpper(target.Purpose)) {
		if item.ID == target.ID {
			return
		}
	}
	t.Fatalf("search did not find %q", target.Purpose)
}

func TestSetTripStatus(t *testing.T) {
	svc := seeded(t)
	last := model.TripStatusValues[len(model.TripStatusValues)-1]
	item, err := svc.SetTripStatus(1, last)
	if err != nil || item.Status != last {
		t.Fatalf("set = %v, %v", item.Status, err)
	}
	if got, want := svc.Trips.CountByStatus()[last], len(svc.Trips.WithStatus(last)); got != want {
		t.Fatalf("count %d != %d", got, want)
	}
}

func TestDeleteTrip(t *testing.T) {
	svc := seeded(t)
	item, err := svc.CreateTrip(service.SampleTrip(14))
	if err != nil {
		t.Fatalf("create: %v", err)
	}
	if err := svc.DeleteTrip(item.ID); err != nil {
		t.Fatalf("delete: %v", err)
	}
	if _, err := svc.GetTrip(item.ID); !errors.Is(err, service.ErrNotFound) {
		t.Fatalf("still there: %v", err)
	}
}
