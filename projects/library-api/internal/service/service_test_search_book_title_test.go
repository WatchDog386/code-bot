package service_test

import (
	"strings"
	"testing"

	"library-api/internal/service"
)

func TestSearchBookTitle(t *testing.T) {
	svc := seeded(t)
	target, _ := svc.GetBook(2)
	for _, item := range svc.Books.SearchTitle(strings.ToUpper(target.Title)) {
		if item.ID == target.ID {
			return
		}
	}
	t.Fatalf("search did not find %q", target.Title)
}

func TestSearchBookIsbn(t *testing.T) {
	svc := seeded(t)
	target, _ := svc.GetBook(2)
	for _, item := range svc.Books.SearchIsbn(strings.ToUpper(target.Isbn)) {
		if item.ID == target.ID {
			return
		}
	}
	t.Fatalf("search did not find %q", target.Isbn)
}

func TestAdjustBookPages(t *testing.T) {
	svc := seeded(t)
	before, _ := svc.GetBook(1)
	after, err := svc.AdjustBookPages(1, 2)
	if err != nil || after.Pages != before.Pages+2 {
		t.Fatalf("adjust = %v, %v", after.Pages, err)
	}
	_, err = svc.AdjustBookPages(1, -(after.Pages + 100))
	wantField(t, err, "pages")
}

func TestAdjustBookPrice(t *testing.T) {
	svc := seeded(t)
	before, _ := svc.GetBook(1)
	after, err := svc.AdjustBookPrice(1, 1.5)
	if err != nil || after.Price-before.Price < 1.49 || after.Price-before.Price > 1.51 {
		t.Fatalf("adjust = %v, %v", after.Price, err)
	}
}

func TestBookPublishedRanges(t *testing.T) {
	svc := seeded(t)
	day := service.SampleBook(2).Published
	total := len(svc.Books.PublishedBefore(day)) + len(svc.Books.PublishedOn(day)) + len(svc.Books.PublishedAfter(day))
	if total != svc.Books.Count() {
		t.Fatalf("ranges cover %d of %d records", total, svc.Books.Count())
	}
}
