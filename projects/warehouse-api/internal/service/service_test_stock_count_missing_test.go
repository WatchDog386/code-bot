package service_test

import (
	"errors"
	"testing"

	"warehouse-api/internal/service"
)

func TestStockCountMissing(t *testing.T) {
	svc := seeded(t)
	if _, err := svc.GetStockCount(9999); !errors.Is(err, service.ErrNotFound) {
		t.Fatalf("want ErrNotFound, got %v", err)
	}
}

func TestStockCountRejectsBadBinID(t *testing.T) {
	svc := seeded(t)
	item := service.SampleStockCount(12)
	item.BinID = 0
	_, err := svc.CreateStockCount(item)
	wantField(t, err, "bin_id")
}

func TestStockCountRejectsBadProductID(t *testing.T) {
	svc := seeded(t)
	item := service.SampleStockCount(12)
	item.ProductID = 0
	_, err := svc.CreateStockCount(item)
	wantField(t, err, "product_id")
}
