package service_test

import (
	"errors"
	"strings"
	"testing"

	"warehouse-api/internal/service"
)

func TestPurchaseOrderRejectsBadOrdered(t *testing.T) {
	svc := seeded(t)
	item := service.SamplePurchaseOrder(12)
	item.Ordered = "2026-02-30"
	_, err := svc.CreatePurchaseOrder(item)
	wantField(t, err, "ordered")
}

func TestPurchaseOrderRejectsBadExpected(t *testing.T) {
	svc := seeded(t)
	item := service.SamplePurchaseOrder(12)
	item.Expected = "2026-02-30"
	_, err := svc.CreatePurchaseOrder(item)
	wantField(t, err, "expected")
}

func TestPurchaseOrderRejectsBadTotal(t *testing.T) {
	svc := seeded(t)
	item := service.SamplePurchaseOrder(12)
	item.Total = -5
	_, err := svc.CreatePurchaseOrder(item)
	wantField(t, err, "total")
}

func TestPurchaseOrderRejectsBadStatus(t *testing.T) {
	svc := seeded(t)
	item := service.SamplePurchaseOrder(12)
	item.Status = "nope"
	_, err := svc.CreatePurchaseOrder(item)
	wantField(t, err, "status")
}

func TestPurchaseOrderRejectsBadNotes(t *testing.T) {
	svc := seeded(t)
	item := service.SamplePurchaseOrder(12)
	item.Notes = strings.Repeat("x", 3000)
	_, err := svc.CreatePurchaseOrder(item)
	wantField(t, err, "notes")
}

func TestPurchaseOrderSupplierIDMustExist(t *testing.T) {
	svc := seeded(t)
	item := service.SamplePurchaseOrder(13)
	item.SupplierID = 9999
	if _, err := svc.CreatePurchaseOrder(item); !errors.Is(err, service.ErrNotFound) {
		t.Fatalf("want ErrNotFound, got %v", err)
	}
}

func TestPurchaseOrderOrderedRanges(t *testing.T) {
	svc := seeded(t)
	day := service.SamplePurchaseOrder(2).Ordered
	total := len(svc.PurchaseOrders.OrderedBefore(day)) + len(svc.PurchaseOrders.OrderedOn(day)) + len(svc.PurchaseOrders.OrderedAfter(day))
	if total != svc.PurchaseOrders.Count() {
		t.Fatalf("ranges cover %d of %d records", total, svc.PurchaseOrders.Count())
	}
}
