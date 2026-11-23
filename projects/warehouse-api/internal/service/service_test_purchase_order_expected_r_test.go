package service_test

import (
	"testing"

	"warehouse-api/internal/service"
)

func TestPurchaseOrderExpectedRanges(t *testing.T) {
	svc := seeded(t)
	day := service.SamplePurchaseOrder(2).Expected
	total := len(svc.PurchaseOrders.ExpectedBefore(day)) + len(svc.PurchaseOrders.ExpectedOn(day)) + len(svc.PurchaseOrders.ExpectedAfter(day))
	if total != svc.PurchaseOrders.Count() {
		t.Fatalf("ranges cover %d of %d records", total, svc.PurchaseOrders.Count())
	}
}

func TestAdjustPurchaseOrderTotal(t *testing.T) {
	svc := seeded(t)
	before, _ := svc.GetPurchaseOrder(1)
	after, err := svc.AdjustPurchaseOrderTotal(1, 1.5)
	if err != nil || after.Total-before.Total < 1.49 || after.Total-before.Total > 1.51 {
		t.Fatalf("adjust = %v, %v", after.Total, err)
	}
}
