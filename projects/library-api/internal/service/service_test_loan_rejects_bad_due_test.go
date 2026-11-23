package service_test

import (
	"testing"

	"library-api/internal/service"
)

func TestLoanRejectsBadDue(t *testing.T) {
	svc := seeded(t)
	item := service.SampleLoan(12)
	item.Due = "2026-02-30"
	_, err := svc.CreateLoan(item)
	wantField(t, err, "due")
}

func TestLoanRejectsBadRenewals(t *testing.T) {
	svc := seeded(t)
	item := service.SampleLoan(12)
	item.Renewals = -1
	_, err := svc.CreateLoan(item)
	wantField(t, err, "renewals")
}

func TestLoanRejectsBadStatus(t *testing.T) {
	svc := seeded(t)
	item := service.SampleLoan(12)
	item.Status = "nope"
	_, err := svc.CreateLoan(item)
	wantField(t, err, "status")
}

func TestLoanRejectsBadFee(t *testing.T) {
	svc := seeded(t)
	item := service.SampleLoan(12)
	item.Fee = -5
	_, err := svc.CreateLoan(item)
	wantField(t, err, "fee")
}
