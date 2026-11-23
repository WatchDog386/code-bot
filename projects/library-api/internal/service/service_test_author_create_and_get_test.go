package service_test

import (
	"errors"
	"testing"

	"library-api/internal/service"
)

func TestAuthorCreateAndGet(t *testing.T) {
	svc := seeded(t)
	created, err := svc.CreateAuthor(service.SampleAuthor(10))
	if err != nil {
		t.Fatalf("create: %v", err)
	}
	got, err := svc.GetAuthor(created.ID)
	if err != nil || got != created {
		t.Fatalf("get = %+v, %v; want %+v", got, err, created)
	}
	if n := len(svc.ListAuthors()); n != 4 {
		t.Fatalf("list has %d records, want 4", n)
	}
}

func TestAuthorMissing(t *testing.T) {
	svc := seeded(t)
	if _, err := svc.GetAuthor(9999); !errors.Is(err, service.ErrNotFound) {
		t.Fatalf("want ErrNotFound, got %v", err)
	}
}

func TestAuthorRejectsBadName(t *testing.T) {
	svc := seeded(t)
	item := service.SampleAuthor(12)
	item.Name = ""
	_, err := svc.CreateAuthor(item)
	wantField(t, err, "name")
}

func TestAuthorRejectsBadEmail(t *testing.T) {
	svc := seeded(t)
	item := service.SampleAuthor(12)
	item.Email = "not-an-email"
	_, err := svc.CreateAuthor(item)
	wantField(t, err, "email")
}

func TestAuthorRejectsBadCountry(t *testing.T) {
	svc := seeded(t)
	item := service.SampleAuthor(12)
	item.Country = ""
	_, err := svc.CreateAuthor(item)
	wantField(t, err, "country")
}

func TestAuthorRejectsBadBorn(t *testing.T) {
	svc := seeded(t)
	item := service.SampleAuthor(12)
	item.Born = "2026-02-30"
	_, err := svc.CreateAuthor(item)
	wantField(t, err, "born")
}
