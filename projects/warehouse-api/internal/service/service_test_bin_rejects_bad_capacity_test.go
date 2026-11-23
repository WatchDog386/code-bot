package service_test

import (
	"strings"
	"testing"

	"warehouse-api/internal/service"
)

func TestBinRejectsBadCapacity(t *testing.T) {
	svc := seeded(t)
	item := service.SampleBin(12)
	item.Capacity = -1
	_, err := svc.CreateBin(item)
	wantField(t, err, "capacity")
}

func TestSearchBinCode(t *testing.T) {
	svc := seeded(t)
	target, _ := svc.GetBin(2)
	for _, item := range svc.Bins.SearchCode(strings.ToUpper(target.Code)) {
		if item.ID == target.ID {
			return
		}
	}
	t.Fatalf("search did not find %q", target.Code)
}

func TestSearchBinAisle(t *testing.T) {
	svc := seeded(t)
	target, _ := svc.GetBin(2)
	for _, item := range svc.Bins.SearchAisle(strings.ToUpper(target.Aisle)) {
		if item.ID == target.ID {
			return
		}
	}
	t.Fatalf("search did not find %q", target.Aisle)
}

func TestAdjustBinShelf(t *testing.T) {
	svc := seeded(t)
	before, _ := svc.GetBin(1)
	after, err := svc.AdjustBinShelf(1, 2)
	if err != nil || after.Shelf != before.Shelf+2 {
		t.Fatalf("adjust = %v, %v", after.Shelf, err)
	}
	_, err = svc.AdjustBinShelf(1, -(after.Shelf + 100))
	wantField(t, err, "shelf")
}

func TestAdjustBinCapacity(t *testing.T) {
	svc := seeded(t)
	before, _ := svc.GetBin(1)
	after, err := svc.AdjustBinCapacity(1, 2)
	if err != nil || after.Capacity != before.Capacity+2 {
		t.Fatalf("adjust = %v, %v", after.Capacity, err)
	}
	_, err = svc.AdjustBinCapacity(1, -(after.Capacity + 100))
	wantField(t, err, "capacity")
}

func TestToggleBinRefrigerated(t *testing.T) {
	svc := seeded(t)
	before, _ := svc.GetBin(1)
	after, err := svc.ToggleBinRefrigerated(1)
	if err != nil || after.Refrigerated == before.Refrigerated {
		t.Fatalf("toggle = %v, %v", after.Refrigerated, err)
	}
}
