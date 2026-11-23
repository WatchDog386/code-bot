package service_test

import (
	"errors"
	"testing"

	"warehouse-api/internal/service"
)

func TestStockCountRejectsBadCounted(t *testing.T) {
	svc := seeded(t)
	item := service.SampleStockCount(12)
	item.Counted = "2026-02-30"
	_, err := svc.CreateStockCount(item)
	wantField(t, err, "counted")
}

func TestStockCountRejectsBadExpected(t *testing.T) {
	svc := seeded(t)
	item := service.SampleStockCount(12)
	item.Expected = -1
	_, err := svc.CreateStockCount(item)
	wantField(t, err, "expected")
}

func TestStockCountRejectsBadFound(t *testing.T) {
	svc := seeded(t)
	item := service.SampleStockCount(12)
	item.Found = -1
	_, err := svc.CreateStockCount(item)
	wantField(t, err, "found")
}

func TestStockCountRejectsBadCounter(t *testing.T) {
	svc := seeded(t)
	item := service.SampleStockCount(12)
	item.Counter = ""
	_, err := svc.CreateStockCount(item)
	wantField(t, err, "counter")
}

func TestStockCountBinIDMustExist(t *testing.T) {
	svc := seeded(t)
	item := service.SampleStockCount(13)
	item.BinID = 9999
	if _, err := svc.CreateStockCount(item); !errors.Is(err, service.ErrNotFound) {
		t.Fatalf("want ErrNotFound, got %v", err)
	}
}

func TestStockCountProductIDMustExist(t *testing.T) {
	svc := seeded(t)
	item := service.SampleStockCount(13)
	item.ProductID = 9999
	if _, err := svc.CreateStockCount(item); !errors.Is(err, service.ErrNotFound) {
		t.Fatalf("want ErrNotFound, got %v", err)
	}
}

func TestStockCountCountedRanges(t *testing.T) {
	svc := seeded(t)
	day := service.SampleStockCount(2).Counted
	total := len(svc.StockCounts.CountedBefore(day)) + len(svc.StockCounts.CountedOn(day)) + len(svc.StockCounts.CountedAfter(day))
	if total != svc.StockCounts.Count() {
		t.Fatalf("ranges cover %d of %d records", total, svc.StockCounts.Count())
	}
}
