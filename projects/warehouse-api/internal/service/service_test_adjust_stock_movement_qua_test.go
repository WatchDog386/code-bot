package service_test

import (
	"testing"

	"warehouse-api/internal/model"
	"warehouse-api/internal/service"
)

func TestAdjustStockMovementQuantity(t *testing.T) {
	svc := seeded(t)
	before, _ := svc.GetStockMovement(1)
	after, err := svc.AdjustStockMovementQuantity(1, 2)
	if err != nil || after.Quantity != before.Quantity+2 {
		t.Fatalf("adjust = %v, %v", after.Quantity, err)
	}
	_, err = svc.AdjustStockMovementQuantity(1, -(after.Quantity + 100))
	wantField(t, err, "quantity")
}

func TestStockMovementMovedRanges(t *testing.T) {
	svc := seeded(t)
	day := service.SampleStockMovement(2).Moved
	total := len(svc.StockMovements.MovedBefore(day)) + len(svc.StockMovements.MovedOn(day)) + len(svc.StockMovements.MovedAfter(day))
	if total != svc.StockMovements.Count() {
		t.Fatalf("ranges cover %d of %d records", total, svc.StockMovements.Count())
	}
}

func TestSetStockMovementReason(t *testing.T) {
	svc := seeded(t)
	last := model.StockMovementReasonValues[len(model.StockMovementReasonValues)-1]
	item, err := svc.SetStockMovementReason(1, last)
	if err != nil || item.Reason != last {
		t.Fatalf("set = %v, %v", item.Reason, err)
	}
	if got, want := svc.StockMovements.CountByReason()[last], len(svc.StockMovements.WithReason(last)); got != want {
		t.Fatalf("count %d != %d", got, want)
	}
}
