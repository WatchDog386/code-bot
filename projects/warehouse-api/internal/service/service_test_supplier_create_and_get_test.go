package service_test

import (
	"errors"
	"testing"

	"warehouse-api/internal/service"
)

func TestSupplierCreateAndGet(t *testing.T) {
	svc := seeded(t)
	created, err := svc.CreateSupplier(service.SampleSupplier(10))
	if err != nil {
		t.Fatalf("create: %v", err)
	}
	got, err := svc.GetSupplier(created.ID)
	if err != nil || got != created {
		t.Fatalf("get = %+v, %v; want %+v", got, err, created)
	}
	if n := len(svc.ListSuppliers()); n != 4 {
		t.Fatalf("list has %d records, want 4", n)
	}
}

func TestSupplierMissing(t *testing.T) {
	svc := seeded(t)
	if _, err := svc.GetSupplier(9999); !errors.Is(err, service.ErrNotFound) {
		t.Fatalf("want ErrNotFound, got %v", err)
	}
}

func TestSupplierRejectsBadName(t *testing.T) {
	svc := seeded(t)
	item := service.SampleSupplier(12)
	item.Name = ""
	_, err := svc.CreateSupplier(item)
	wantField(t, err, "name")
}

func TestSupplierRejectsBadEmail(t *testing.T) {
	svc := seeded(t)
	item := service.SampleSupplier(12)
	item.Email = "not-an-email"
	_, err := svc.CreateSupplier(item)
	wantField(t, err, "email")
}

func TestSupplierRejectsBadPhone(t *testing.T) {
	svc := seeded(t)
	item := service.SampleSupplier(12)
	item.Phone = ""
	_, err := svc.CreateSupplier(item)
	wantField(t, err, "phone")
}

func TestSupplierRejectsBadCountry(t *testing.T) {
	svc := seeded(t)
	item := service.SampleSupplier(12)
	item.Country = ""
	_, err := svc.CreateSupplier(item)
	wantField(t, err, "country")
}
