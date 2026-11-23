package service_test

import (
	"errors"
	"testing"

	"library-api/internal/service"
)

func TestLoanCreateAndGet(t *testing.T) {
	svc := seeded(t)
	created, err := svc.CreateLoan(service.SampleLoan(10))
	if err != nil {
		t.Fatalf("create: %v", err)
	}
	got, err := svc.GetLoan(created.ID)
	if err != nil || got != created {
		t.Fatalf("get = %+v, %v; want %+v", got, err, created)
	}
	if n := len(svc.ListLoans()); n != 4 {
		t.Fatalf("list has %d records, want 4", n)
	}
}

func TestLoanMissing(t *testing.T) {
	svc := seeded(t)
	if _, err := svc.GetLoan(9999); !errors.Is(err, service.ErrNotFound) {
		t.Fatalf("want ErrNotFound, got %v", err)
	}
}

func TestLoanRejectsBadBookID(t *testing.T) {
	svc := seeded(t)
	item := service.SampleLoan(12)
	item.BookID = 0
	_, err := svc.CreateLoan(item)
	wantField(t, err, "book_id")
}

func TestLoanRejectsBadMemberID(t *testing.T) {
	svc := seeded(t)
	item := service.SampleLoan(12)
	item.MemberID = 0
	_, err := svc.CreateLoan(item)
	wantField(t, err, "member_id")
}

func TestLoanRejectsBadBorrowed(t *testing.T) {
	svc := seeded(t)
	item := service.SampleLoan(12)
	item.Borrowed = "2026-02-30"
	_, err := svc.CreateLoan(item)
	wantField(t, err, "borrowed")
}
