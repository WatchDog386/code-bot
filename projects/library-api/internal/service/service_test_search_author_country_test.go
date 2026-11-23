package service_test

import (
	"errors"
	"strings"
	"testing"

	"library-api/internal/service"
)

func TestSearchAuthorCountry(t *testing.T) {
	svc := seeded(t)
	target, _ := svc.GetAuthor(2)
	for _, item := range svc.Authors.SearchCountry(strings.ToUpper(target.Country)) {
		if item.ID == target.ID {
			return
		}
	}
	t.Fatalf("search did not find %q", target.Country)
}

func TestAuthorBornRanges(t *testing.T) {
	svc := seeded(t)
	day := service.SampleAuthor(2).Born
	total := len(svc.Authors.BornBefore(day)) + len(svc.Authors.BornOn(day)) + len(svc.Authors.BornAfter(day))
	if total != svc.Authors.Count() {
		t.Fatalf("ranges cover %d of %d records", total, svc.Authors.Count())
	}
}

func TestToggleAuthorActive(t *testing.T) {
	svc := seeded(t)
	before, _ := svc.GetAuthor(1)
	after, err := svc.ToggleAuthorActive(1)
	if err != nil || after.Active == before.Active {
		t.Fatalf("toggle = %v, %v", after.Active, err)
	}
}

func TestDeleteAuthor(t *testing.T) {
	svc := seeded(t)
	item, err := svc.CreateAuthor(service.SampleAuthor(14))
	if err != nil {
		t.Fatalf("create: %v", err)
	}
	if err := svc.DeleteAuthor(item.ID); err != nil {
		t.Fatalf("delete: %v", err)
	}
	if _, err := svc.GetAuthor(item.ID); !errors.Is(err, service.ErrNotFound) {
		t.Fatalf("still there: %v", err)
	}
}

func TestDeleteAuthorInUse(t *testing.T) {
	svc := seeded(t)
	if err := svc.DeleteAuthor(1); !errors.Is(err, service.ErrConflict) {
		t.Fatalf("want ErrConflict, got %v", err)
	}
}

func TestAuthorStats(t *testing.T) {
	svc := seeded(t)
	if got := svc.AuthorStats().Count; got != 3 {
		t.Fatalf("count = %d", got)
	}
}
