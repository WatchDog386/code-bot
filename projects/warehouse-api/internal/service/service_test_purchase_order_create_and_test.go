package service_test

import (
	"errors"
	"testing"

	"warehouse-api/internal/service"
)

func TestPurchaseOrderCreateAndGet(t *testing.T) {
	svc := seeded(t)
	created, err := svc.CreatePurchaseOrder(service.SamplePurchaseOrder(10))
	if err != nil {
		t.Fatalf("create: %v", err)
	}
	got, err := svc.GetPurchaseOrder(created.ID)
	if err != nil || got != created {
		t.Fatalf("get = %+v, %v; want %+v", got, err, created)
	}
	if n := len(svc.ListPurchaseOrders()); n != 4 {
		t.Fatalf("list has %d records, want 4", n)
	}
}

func TestPurchaseOrderMissing(t *testing.T) {
	svc := seeded(t)
	if _, err := svc.GetPurchaseOrder(9999); !errors.Is(err, service.ErrNotFound) {
		t.Fatalf("want ErrNotFound, got %v", err)
	}
}

func TestPurchaseOrderRejectsBadSupplierID(t *testing.T) {
	svc := seeded(t)
	item := service.SamplePurchaseOrder(12)
	item.SupplierID = 0
	_, err := svc.CreatePurchaseOrder(item)
	wantField(t, err, "supplier_id")
}
