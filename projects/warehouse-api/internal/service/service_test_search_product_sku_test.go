package service_test

import (
	"strings"
	"testing"
)

func TestSearchProductSku(t *testing.T) {
	svc := seeded(t)
	target, _ := svc.GetProduct(2)
	for _, item := range svc.Products.SearchSku(strings.ToUpper(target.Sku)) {
		if item.ID == target.ID {
			return
		}
	}
	t.Fatalf("search did not find %q", target.Sku)
}

func TestSearchProductName(t *testing.T) {
	svc := seeded(t)
	target, _ := svc.GetProduct(2)
	for _, item := range svc.Products.SearchName(strings.ToUpper(target.Name)) {
		if item.ID == target.ID {
			return
		}
	}
	t.Fatalf("search did not find %q", target.Name)
}

func TestAdjustProductUnitCost(t *testing.T) {
	svc := seeded(t)
	before, _ := svc.GetProduct(1)
	after, err := svc.AdjustProductUnitCost(1, 1.5)
	if err != nil || after.UnitCost-before.UnitCost < 1.49 || after.UnitCost-before.UnitCost > 1.51 {
		t.Fatalf("adjust = %v, %v", after.UnitCost, err)
	}
}

func TestAdjustProductUnitPrice(t *testing.T) {
	svc := seeded(t)
	before, _ := svc.GetProduct(1)
	after, err := svc.AdjustProductUnitPrice(1, 1.5)
	if err != nil || after.UnitPrice-before.UnitPrice < 1.49 || after.UnitPrice-before.UnitPrice > 1.51 {
		t.Fatalf("adjust = %v, %v", after.UnitPrice, err)
	}
}

func TestAdjustProductReorderLevel(t *testing.T) {
	svc := seeded(t)
	before, _ := svc.GetProduct(1)
	after, err := svc.AdjustProductReorderLevel(1, 2)
	if err != nil || after.ReorderLevel != before.ReorderLevel+2 {
		t.Fatalf("adjust = %v, %v", after.ReorderLevel, err)
	}
	_, err = svc.AdjustProductReorderLevel(1, -(after.ReorderLevel + 100))
	wantField(t, err, "reorder_level")
}
