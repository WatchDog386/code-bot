package service_test

import (
	"encoding/json"
	"errors"
	"fmt"
	"net/http"
	"testing"

	"library-api/internal/httpapi"
	"library-api/internal/model"
	"library-api/internal/service"
)

func TestLoanAPI(t *testing.T) {
	h := httpapi.New(seeded(t))
	rec := call(t, h, http.MethodPost, "/loans", service.SampleLoan(15))
	if rec.Code != http.StatusCreated {
		t.Fatalf("POST = %d %s", rec.Code, rec.Body)
	}
	var created model.Loan
	if err := json.Unmarshal(rec.Body.Bytes(), &created); err != nil {
		t.Fatalf("decode: %v", err)
	}
	path := fmt.Sprintf("/loans/%d", created.ID)
	if rec := call(t, h, http.MethodGet, path, nil); rec.Code != http.StatusOK {
		t.Fatalf("GET = %d", rec.Code)
	}
	if rec := call(t, h, http.MethodGet, "/loans?size=2&page=1", nil); rec.Code != http.StatusOK {
		t.Fatalf("list = %d", rec.Code)
	}
	if rec := call(t, h, http.MethodGet, "/loans/stats", nil); rec.Code != http.StatusOK {
		t.Fatalf("stats = %d", rec.Code)
	}
	if rec := call(t, h, http.MethodPost, "/loans", map[string]int{"no_such_field": 1}); rec.Code != http.StatusBadRequest {
		t.Fatalf("bad POST = %d", rec.Code)
	}
	if rec := call(t, h, http.MethodDelete, path, nil); rec.Code != http.StatusNoContent {
		t.Fatalf("DELETE = %d", rec.Code)
	}
	if rec := call(t, h, http.MethodGet, path, nil); rec.Code != http.StatusNotFound {
		t.Fatalf("GET after delete = %d", rec.Code)
	}
}

func TestReservationCreateAndGet(t *testing.T) {
	svc := seeded(t)
	created, err := svc.CreateReservation(service.SampleReservation(10))
	if err != nil {
		t.Fatalf("create: %v", err)
	}
	got, err := svc.GetReservation(created.ID)
	if err != nil || got != created {
		t.Fatalf("get = %+v, %v; want %+v", got, err, created)
	}
	if n := len(svc.ListReservations()); n != 4 {
		t.Fatalf("list has %d records, want 4", n)
	}
}

func TestReservationMissing(t *testing.T) {
	svc := seeded(t)
	if _, err := svc.GetReservation(9999); !errors.Is(err, service.ErrNotFound) {
		t.Fatalf("want ErrNotFound, got %v", err)
	}
}

func TestReservationRejectsBadBookID(t *testing.T) {
	svc := seeded(t)
	item := service.SampleReservation(12)
	item.BookID = 0
	_, err := svc.CreateReservation(item)
	wantField(t, err, "book_id")
}
