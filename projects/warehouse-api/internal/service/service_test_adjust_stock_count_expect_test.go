package service_test

import (
	"errors"
	"strings"
	"testing"

	"warehouse-api/internal/service"
)

func TestAdjustStockCountExpected(t *testing.T) {
	svc := seeded(t)
	before, _ := svc.GetStockCount(1)
	after, err := svc.AdjustStockCountExpected(1, 2)
	if err != nil || after.Expected != before.Expected+2 {
		t.Fatalf("adjust = %v, %v", after.Expected, err)
	}
	_, err = svc.AdjustStockCountExpected(1, -(after.Expected + 100))
	wantField(t, err, "expected")
}

func TestAdjustStockCountFound(t *testing.T) {
	svc := seeded(t)
	before, _ := svc.GetStockCount(1)
	after, err := svc.AdjustStockCountFound(1, 2)
	if err != nil || after.Found != before.Found+2 {
		t.Fatalf("adjust = %v, %v", after.Found, err)
	}
	_, err = svc.AdjustStockCountFound(1, -(after.Found + 100))
	wantField(t, err, "found")
}

func TestSearchStockCountCounter(t *testing.T) {
	svc := seeded(t)
	target, _ := svc.GetStockCount(2)
	for _, item := range svc.StockCounts.SearchCounter(strings.ToUpper(target.Counter)) {
		if item.ID == target.ID {
			return
		}
	}
	t.Fatalf("search did not find %q", target.Counter)
}

func TestDeleteStockCount(t *testing.T) {
	svc := seeded(t)
	item, err := svc.CreateStockCount(service.SampleStockCount(14))
	if err != nil {
		t.Fatalf("create: %v", err)
	}
	if err := svc.DeleteStockCount(item.ID); err != nil {
		t.Fatalf("delete: %v", err)
	}
	if _, err := svc.GetStockCount(item.ID); !errors.Is(err, service.ErrNotFound) {
		t.Fatalf("still there: %v", err)
	}
}
