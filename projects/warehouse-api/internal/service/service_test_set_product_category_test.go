package service_test

import (
	"errors"
	"testing"

	"warehouse-api/internal/model"
	"warehouse-api/internal/service"
)

func TestSetProductCategory(t *testing.T) {
	svc := seeded(t)
	last := model.ProductCategoryValues[len(model.ProductCategoryValues)-1]
	item, err := svc.SetProductCategory(1, last)
	if err != nil || item.Category != last {
		t.Fatalf("set = %v, %v", item.Category, err)
	}
	if got, want := svc.Products.CountByCategory()[last], len(svc.Products.WithCategory(last)); got != want {
		t.Fatalf("count %d != %d", got, want)
	}
}

func TestToggleProductActive(t *testing.T) {
	svc := seeded(t)
	before, _ := svc.GetProduct(1)
	after, err := svc.ToggleProductActive(1)
	if err != nil || after.Active == before.Active {
		t.Fatalf("toggle = %v, %v", after.Active, err)
	}
}

func TestDeleteProduct(t *testing.T) {
	svc := seeded(t)
	item, err := svc.CreateProduct(service.SampleProduct(14))
	if err != nil {
		t.Fatalf("create: %v", err)
	}
	if err := svc.DeleteProduct(item.ID); err != nil {
		t.Fatalf("delete: %v", err)
	}
	if _, err := svc.GetProduct(item.ID); !errors.Is(err, service.ErrNotFound) {
		t.Fatalf("still there: %v", err)
	}
}

func TestDeleteProductInUse(t *testing.T) {
	svc := seeded(t)
	if err := svc.DeleteProduct(1); !errors.Is(err, service.ErrConflict) {
		t.Fatalf("want ErrConflict, got %v", err)
	}
}

func TestProductStats(t *testing.T) {
	svc := seeded(t)
	if got := svc.ProductStats().Count; got != 3 {
		t.Fatalf("count = %d", got)
	}
}
