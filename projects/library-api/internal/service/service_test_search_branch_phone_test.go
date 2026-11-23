package service_test

import (
	"errors"
	"strings"
	"testing"

	"library-api/internal/service"
)

func TestSearchBranchPhone(t *testing.T) {
	svc := seeded(t)
	target, _ := svc.GetBranch(2)
	for _, item := range svc.Branches.SearchPhone(strings.ToUpper(target.Phone)) {
		if item.ID == target.ID {
			return
		}
	}
	t.Fatalf("search did not find %q", target.Phone)
}

func TestBranchOpenedRanges(t *testing.T) {
	svc := seeded(t)
	day := service.SampleBranch(2).Opened
	total := len(svc.Branches.OpenedBefore(day)) + len(svc.Branches.OpenedOn(day)) + len(svc.Branches.OpenedAfter(day))
	if total != svc.Branches.Count() {
		t.Fatalf("ranges cover %d of %d records", total, svc.Branches.Count())
	}
}

func TestAdjustBranchSeats(t *testing.T) {
	svc := seeded(t)
	before, _ := svc.GetBranch(1)
	after, err := svc.AdjustBranchSeats(1, 2)
	if err != nil || after.Seats != before.Seats+2 {
		t.Fatalf("adjust = %v, %v", after.Seats, err)
	}
	_, err = svc.AdjustBranchSeats(1, -(after.Seats + 100))
	wantField(t, err, "seats")
}

func TestToggleBranchOpenLate(t *testing.T) {
	svc := seeded(t)
	before, _ := svc.GetBranch(1)
	after, err := svc.ToggleBranchOpenLate(1)
	if err != nil || after.OpenLate == before.OpenLate {
		t.Fatalf("toggle = %v, %v", after.OpenLate, err)
	}
}

func TestDeleteBranch(t *testing.T) {
	svc := seeded(t)
	item, err := svc.CreateBranch(service.SampleBranch(14))
	if err != nil {
		t.Fatalf("create: %v", err)
	}
	if err := svc.DeleteBranch(item.ID); err != nil {
		t.Fatalf("delete: %v", err)
	}
	if _, err := svc.GetBranch(item.ID); !errors.Is(err, service.ErrNotFound) {
		t.Fatalf("still there: %v", err)
	}
}
