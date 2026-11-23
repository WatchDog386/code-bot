package service_test

import (
	"strings"
	"testing"

	"library-api/internal/service"
)

func TestBranchRejectsBadPhone(t *testing.T) {
	svc := seeded(t)
	item := service.SampleBranch(12)
	item.Phone = ""
	_, err := svc.CreateBranch(item)
	wantField(t, err, "phone")
}

func TestBranchRejectsBadOpened(t *testing.T) {
	svc := seeded(t)
	item := service.SampleBranch(12)
	item.Opened = "2026-02-30"
	_, err := svc.CreateBranch(item)
	wantField(t, err, "opened")
}

func TestBranchRejectsBadSeats(t *testing.T) {
	svc := seeded(t)
	item := service.SampleBranch(12)
	item.Seats = -1
	_, err := svc.CreateBranch(item)
	wantField(t, err, "seats")
}

func TestSearchBranchName(t *testing.T) {
	svc := seeded(t)
	target, _ := svc.GetBranch(2)
	for _, item := range svc.Branches.SearchName(strings.ToUpper(target.Name)) {
		if item.ID == target.ID {
			return
		}
	}
	t.Fatalf("search did not find %q", target.Name)
}

func TestSearchBranchCity(t *testing.T) {
	svc := seeded(t)
	target, _ := svc.GetBranch(2)
	for _, item := range svc.Branches.SearchCity(strings.ToUpper(target.City)) {
		if item.ID == target.ID {
			return
		}
	}
	t.Fatalf("search did not find %q", target.City)
}
