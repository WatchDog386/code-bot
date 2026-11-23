package service_test

import (
	"errors"
	"strings"
	"testing"

	"library-api/internal/service"
)

func TestReservationRejectsBadStatus(t *testing.T) {
	svc := seeded(t)
	item := service.SampleReservation(12)
	item.Status = "nope"
	_, err := svc.CreateReservation(item)
	wantField(t, err, "status")
}

func TestReservationRejectsBadNotes(t *testing.T) {
	svc := seeded(t)
	item := service.SampleReservation(12)
	item.Notes = strings.Repeat("x", 3000)
	_, err := svc.CreateReservation(item)
	wantField(t, err, "notes")
}

func TestReservationBookIDMustExist(t *testing.T) {
	svc := seeded(t)
	item := service.SampleReservation(13)
	item.BookID = 9999
	if _, err := svc.CreateReservation(item); !errors.Is(err, service.ErrNotFound) {
		t.Fatalf("want ErrNotFound, got %v", err)
	}
}
