package service_test

import (
	"errors"
	"testing"

	"warehouse-api/internal/service"
)

func TestStockMovementCreateAndGet(t *testing.T) {
	svc := seeded(t)
	created, err := svc.CreateStockMovement(service.SampleStockMovement(10))
	if err != nil {
		t.Fatalf("create: %v", err)
	}
	got, err := svc.GetStockMovement(created.ID)
	if err != nil || got != created {
		t.Fatalf("get = %+v, %v; want %+v", got, err, created)
	}
	if n := len(svc.ListStockMovements()); n != 4 {
		t.Fatalf("list has %d records, want 4", n)
	}
}

func TestStockMovementMissing(t *testing.T) {
	svc := seeded(t)
	if _, err := svc.GetStockMovement(9999); !errors.Is(err, service.ErrNotFound) {
		t.Fatalf("want ErrNotFound, got %v", err)
	}
}

func TestStockMovementRejectsBadProductID(t *testing.T) {
	svc := seeded(t)
	item := service.SampleStockMovement(12)
	item.ProductID = 0
	_, err := svc.CreateStockMovement(item)
	wantField(t, err, "product_id")
}

func TestStockMovementRejectsBadBinID(t *testing.T) {
	svc := seeded(t)
	item := service.SampleStockMovement(12)
	item.BinID = 0
	_, err := svc.CreateStockMovement(item)
	wantField(t, err, "bin_id")
}
