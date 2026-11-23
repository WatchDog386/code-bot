package service_test

import (
	"testing"

	"library-api/internal/service"
)

func TestReservationRejectsBadMemberID(t *testing.T) {
	svc := seeded(t)
	item := service.SampleReservation(12)
	item.MemberID = 0
	_, err := svc.CreateReservation(item)
	wantField(t, err, "member_id")
}

func TestReservationRejectsBadRequested(t *testing.T) {
	svc := seeded(t)
	item := service.SampleReservation(12)
	item.Requested = "2026-02-30"
	_, err := svc.CreateReservation(item)
	wantField(t, err, "requested")
}

func TestReservationRejectsBadPosition(t *testing.T) {
	svc := seeded(t)
	item := service.SampleReservation(12)
	item.Position = -1
	_, err := svc.CreateReservation(item)
	wantField(t, err, "position")
}
