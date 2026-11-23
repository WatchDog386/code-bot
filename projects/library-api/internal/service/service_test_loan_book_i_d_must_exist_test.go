package service_test

import (
	"errors"
	"testing"

	"library-api/internal/model"
	"library-api/internal/service"
)

func TestLoanBookIDMustExist(t *testing.T) {
	svc := seeded(t)
	item := service.SampleLoan(13)
	item.BookID = 9999
	if _, err := svc.CreateLoan(item); !errors.Is(err, service.ErrNotFound) {
		t.Fatalf("want ErrNotFound, got %v", err)
	}
}

func TestLoanMemberIDMustExist(t *testing.T) {
	svc := seeded(t)
	item := service.SampleLoan(13)
	item.MemberID = 9999
	if _, err := svc.CreateLoan(item); !errors.Is(err, service.ErrNotFound) {
		t.Fatalf("want ErrNotFound, got %v", err)
	}
}

func TestLoanBorrowedRanges(t *testing.T) {
	svc := seeded(t)
	day := service.SampleLoan(2).Borrowed
	total := len(svc.Loans.BorrowedBefore(day)) + len(svc.Loans.BorrowedOn(day)) + len(svc.Loans.BorrowedAfter(day))
	if total != svc.Loans.Count() {
		t.Fatalf("ranges cover %d of %d records", total, svc.Loans.Count())
	}
}

func TestLoanDueRanges(t *testing.T) {
	svc := seeded(t)
	day := service.SampleLoan(2).Due
	total := len(svc.Loans.DueBefore(day)) + len(svc.Loans.DueOn(day)) + len(svc.Loans.DueAfter(day))
	if total != svc.Loans.Count() {
		t.Fatalf("ranges cover %d of %d records", total, svc.Loans.Count())
	}
}

func TestAdjustLoanRenewals(t *testing.T) {
	svc := seeded(t)
	before, _ := svc.GetLoan(1)
	after, err := svc.AdjustLoanRenewals(1, 2)
	if err != nil || after.Renewals != before.Renewals+2 {
		t.Fatalf("adjust = %v, %v", after.Renewals, err)
	}
	_, err = svc.AdjustLoanRenewals(1, -(after.Renewals + 100))
	wantField(t, err, "renewals")
}

func TestSetLoanStatus(t *testing.T) {
	svc := seeded(t)
	last := model.LoanStatusValues[len(model.LoanStatusValues)-1]
	item, err := svc.SetLoanStatus(1, last)
	if err != nil || item.Status != last {
		t.Fatalf("set = %v, %v", item.Status, err)
	}
	if got, want := svc.Loans.CountByStatus()[last], len(svc.Loans.WithStatus(last)); got != want {
		t.Fatalf("count %d != %d", got, want)
	}
}

func TestAdjustLoanFee(t *testing.T) {
	svc := seeded(t)
	before, _ := svc.GetLoan(1)
	after, err := svc.AdjustLoanFee(1, 1.5)
	if err != nil || after.Fee-before.Fee < 1.49 || after.Fee-before.Fee > 1.51 {
		t.Fatalf("adjust = %v, %v", after.Fee, err)
	}
}
