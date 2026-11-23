package service_test

import (
	"errors"
	"strings"
	"testing"

	"warehouse-api/internal/service"
)

func TestSearchSupplierEmail(t *testing.T) {
	svc := seeded(t)
	target, _ := svc.GetSupplier(2)
	for _, item := range svc.Suppliers.SearchEmail(strings.ToUpper(target.Email)) {
		if item.ID == target.ID {
			return
		}
	}
	t.Fatalf("search did not find %q", target.Email)
}

func TestSearchSupplierPhone(t *testing.T) {
	svc := seeded(t)
	target, _ := svc.GetSupplier(2)
	for _, item := range svc.Suppliers.SearchPhone(strings.ToUpper(target.Phone)) {
		if item.ID == target.ID {
			return
		}
	}
	t.Fatalf("search did not find %q", target.Phone)
}

func TestSearchSupplierCountry(t *testing.T) {
	svc := seeded(t)
	target, _ := svc.GetSupplier(2)
	for _, item := range svc.Suppliers.SearchCountry(strings.ToUpper(target.Country)) {
		if item.ID == target.ID {
			return
		}
	}
	t.Fatalf("search did not find %q", target.Country)
}

func TestAdjustSupplierLeadDays(t *testing.T) {
	svc := seeded(t)
	before, _ := svc.GetSupplier(1)
	after, err := svc.AdjustSupplierLeadDays(1, 2)
	if err != nil || after.LeadDays != before.LeadDays+2 {
		t.Fatalf("adjust = %v, %v", after.LeadDays, err)
	}
	_, err = svc.AdjustSupplierLeadDays(1, -(after.LeadDays + 100))
	wantField(t, err, "lead_days")
}

func TestToggleSupplierPreferred(t *testing.T) {
	svc := seeded(t)
	before, _ := svc.GetSupplier(1)
	after, err := svc.ToggleSupplierPreferred(1)
	if err != nil || after.Preferred == before.Preferred {
		t.Fatalf("toggle = %v, %v", after.Preferred, err)
	}
}

func TestDeleteSupplier(t *testing.T) {
	svc := seeded(t)
	item, err := svc.CreateSupplier(service.SampleSupplier(14))
	if err != nil {
		t.Fatalf("create: %v", err)
	}
	if err := svc.DeleteSupplier(item.ID); err != nil {
		t.Fatalf("delete: %v", err)
	}
	if _, err := svc.GetSupplier(item.ID); !errors.Is(err, service.ErrNotFound) {
		t.Fatalf("still there: %v", err)
	}
}
