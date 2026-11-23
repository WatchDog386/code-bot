package service_test

import (
	"errors"
	"strings"
	"testing"

	"library-api/internal/model"
	"library-api/internal/service"
)

func TestReservationMemberIDMustExist(t *testing.T) {
	svc := seeded(t)
	item := service.SampleReservation(13)
	item.MemberID = 9999
	if _, err := svc.CreateReservation(item); !errors.Is(err, service.ErrNotFound) {
		t.Fatalf("want ErrNotFound, got %v", err)
	}
}

func TestReservationRequestedRanges(t *testing.T) {
	svc := seeded(t)
	day := service.SampleReservation(2).Requested
	total := len(svc.Reservations.RequestedBefore(day)) + len(svc.Reservations.RequestedOn(day)) + len(svc.Reservations.RequestedAfter(day))
	if total != svc.Reservations.Count() {
		t.Fatalf("ranges cover %d of %d records", total, svc.Reservations.Count())
	}
}

func TestAdjustReservationPosition(t *testing.T) {
	svc := seeded(t)
	before, _ := svc.GetReservation(1)
	after, err := svc.AdjustReservationPosition(1, 2)
	if err != nil || after.Position != before.Position+2 {
		t.Fatalf("adjust = %v, %v", after.Position, err)
	}
	_, err = svc.AdjustReservationPosition(1, -(after.Position + 100))
	wantField(t, err, "position")
}

func TestSetReservationStatus(t *testing.T) {
	svc := seeded(t)
	last := model.ReservationStatusValues[len(model.ReservationStatusValues)-1]
	item, err := svc.SetReservationStatus(1, last)
	if err != nil || item.Status != last {
		t.Fatalf("set = %v, %v", item.Status, err)
	}
	if got, want := svc.Reservations.CountByStatus()[last], len(svc.Reservations.WithStatus(last)); got != want {
		t.Fatalf("count %d != %d", got, want)
	}
}

func TestSearchReservationNotes(t *testing.T) {
	svc := seeded(t)
	target, _ := svc.GetReservation(2)
	for _, item := range svc.Reservations.SearchNotes(strings.ToUpper(target.Notes)) {
		if item.ID == target.ID {
			return
		}
	}
	t.Fatalf("search did not find %q", target.Notes)
}

func TestDeleteReservation(t *testing.T) {
	svc := seeded(t)
	item, err := svc.CreateReservation(service.SampleReservation(14))
	if err != nil {
		t.Fatalf("create: %v", err)
	}
	if err := svc.DeleteReservation(item.ID); err != nil {
		t.Fatalf("delete: %v", err)
	}
	if _, err := svc.GetReservation(item.ID); !errors.Is(err, service.ErrNotFound) {
		t.Fatalf("still there: %v", err)
	}
}
