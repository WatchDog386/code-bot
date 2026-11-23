package service_test

import (
	"errors"
	"testing"

	"warehouse-api/internal/service"
)

func TestStockMovementRejectsBadQuantity(t *testing.T) {
	svc := seeded(t)
	item := service.SampleStockMovement(12)
	item.Quantity = -1
	_, err := svc.CreateStockMovement(item)
	wantField(t, err, "quantity")
}

func TestStockMovementRejectsBadMoved(t *testing.T) {
	svc := seeded(t)
	item := service.SampleStockMovement(12)
	item.Moved = "2026-02-30"
	_, err := svc.CreateStockMovement(item)
	wantField(t, err, "moved")
}

func TestStockMovementRejectsBadReason(t *testing.T) {
	svc := seeded(t)
	item := service.SampleStockMovement(12)
	item.Reason = "nope"
	_, err := svc.CreateStockMovement(item)
	wantField(t, err, "reason")
}

func TestStockMovementRejectsBadReference(t *testing.T) {
	svc := seeded(t)
	item := service.SampleStockMovement(12)
	item.Reference = ""
	_, err := svc.CreateStockMovement(item)
	wantField(t, err, "reference")
}

func TestStockMovementProductIDMustExist(t *testing.T) {
	svc := seeded(t)
	item := service.SampleStockMovement(13)
	item.ProductID = 9999
	if _, err := svc.CreateStockMovement(item); !errors.Is(err, service.ErrNotFound) {
		t.Fatalf("want ErrNotFound, got %v", err)
	}
}

func TestStockMovementBinIDMustExist(t *testing.T) {
	svc := seeded(t)
	item := service.SampleStockMovement(13)
	item.BinID = 9999
	if _, err := svc.CreateStockMovement(item); !errors.Is(err, service.ErrNotFound) {
		t.Fatalf("want ErrNotFound, got %v", err)
	}
}
