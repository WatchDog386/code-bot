package service_test

import (
	"errors"
	"testing"

	"library-api/internal/service"
)

func TestDeleteLoan(t *testing.T) {
	svc := seeded(t)
	item, err := svc.CreateLoan(service.SampleLoan(14))
	if err != nil {
		t.Fatalf("create: %v", err)
	}
	if err := svc.DeleteLoan(item.ID); err != nil {
		t.Fatalf("delete: %v", err)
	}
	if _, err := svc.GetLoan(item.ID); !errors.Is(err, service.ErrNotFound) {
		t.Fatalf("still there: %v", err)
	}
}

func TestLoanStats(t *testing.T) {
	svc := seeded(t)
	if got := svc.LoanStats().Count; got != 3 {
		t.Fatalf("count = %d", got)
	}
}
