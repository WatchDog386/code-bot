package service_test

import (
	"strings"
	"testing"

	"warehouse-api/internal/model"
)

func TestSetPurchaseOrderStatus(t *testing.T) {
	svc := seeded(t)
	last := model.PurchaseOrderStatusValues[len(model.PurchaseOrderStatusValues)-1]
	item, err := svc.SetPurchaseOrderStatus(1, last)
	if err != nil || item.Status != last {
		t.Fatalf("set = %v, %v", item.Status, err)
	}
	if got, want := svc.PurchaseOrders.CountByStatus()[last], len(svc.PurchaseOrders.WithStatus(last)); got != want {
		t.Fatalf("count %d != %d", got, want)
	}
}

func TestSearchPurchaseOrderNotes(t *testing.T) {
	svc := seeded(t)
	target, _ := svc.GetPurchaseOrder(2)
	for _, item := range svc.PurchaseOrders.SearchNotes(strings.ToUpper(target.Notes)) {
		if item.ID == target.ID {
			return
		}
	}
	t.Fatalf("search did not find %q", target.Notes)
}
