package service_test

import (
	"errors"
	"testing"

	"warehouse-api/internal/service"
)

func TestProductMissing(t *testing.T) {
	svc := seeded(t)
	if _, err := svc.GetProduct(9999); !errors.Is(err, service.ErrNotFound) {
		t.Fatalf("want ErrNotFound, got %v", err)
	}
}

func TestProductRejectsBadSupplierID(t *testing.T) {
	svc := seeded(t)
	item := service.SampleProduct(12)
	item.SupplierID = 0
	_, err := svc.CreateProduct(item)
	wantField(t, err, "supplier_id")
}

func TestProductRejectsBadSku(t *testing.T) {
	svc := seeded(t)
	item := service.SampleProduct(12)
	item.Sku = ""
	_, err := svc.CreateProduct(item)
	wantField(t, err, "sku")
}

func TestProductRejectsBadName(t *testing.T) {
	svc := seeded(t)
	item := service.SampleProduct(12)
	item.Name = ""
	_, err := svc.CreateProduct(item)
	wantField(t, err, "name")
}

func TestProductRejectsBadUnitCost(t *testing.T) {
	svc := seeded(t)
	item := service.SampleProduct(12)
	item.UnitCost = -5
	_, err := svc.CreateProduct(item)
	wantField(t, err, "unit_cost")
}

func TestProductRejectsBadUnitPrice(t *testing.T) {
	svc := seeded(t)
	item := service.SampleProduct(12)
	item.UnitPrice = -5
	_, err := svc.CreateProduct(item)
	wantField(t, err, "unit_price")
}

func TestProductRejectsBadReorderLevel(t *testing.T) {
	svc := seeded(t)
	item := service.SampleProduct(12)
	item.ReorderLevel = -1
	_, err := svc.CreateProduct(item)
	wantField(t, err, "reorder_level")
}

func TestProductRejectsBadCategory(t *testing.T) {
	svc := seeded(t)
	item := service.SampleProduct(12)
	item.Category = "nope"
	_, err := svc.CreateProduct(item)
	wantField(t, err, "category")
}

func TestProductSupplierIDMustExist(t *testing.T) {
	svc := seeded(t)
	item := service.SampleProduct(13)
	item.SupplierID = 9999
	if _, err := svc.CreateProduct(item); !errors.Is(err, service.ErrNotFound) {
		t.Fatalf("want ErrNotFound, got %v", err)
	}
}
