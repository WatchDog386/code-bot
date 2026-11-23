package service_test

import (
	"strings"
	"testing"

	"warehouse-api/internal/service"
)

func TestSupplierRejectsBadLeadDays(t *testing.T) {
	svc := seeded(t)
	item := service.SampleSupplier(12)
	item.LeadDays = -1
	_, err := svc.CreateSupplier(item)
	wantField(t, err, "lead_days")
}

func TestSearchSupplierName(t *testing.T) {
	svc := seeded(t)
	target, _ := svc.GetSupplier(2)
	for _, item := range svc.Suppliers.SearchName(strings.ToUpper(target.Name)) {
		if item.ID == target.ID {
			return
		}
	}
	t.Fatalf("search did not find %q", target.Name)
}
