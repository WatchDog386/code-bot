package service_test

import (
	"errors"
	"testing"

	"library-api/internal/service"
)

func TestBookRejectsBadTitle(t *testing.T) {
	svc := seeded(t)
	item := service.SampleBook(12)
	item.Title = ""
	_, err := svc.CreateBook(item)
	wantField(t, err, "title")
}

func TestBookRejectsBadAuthorID(t *testing.T) {
	svc := seeded(t)
	item := service.SampleBook(12)
	item.AuthorID = 0
	_, err := svc.CreateBook(item)
	wantField(t, err, "author_id")
}

func TestBookRejectsBadIsbn(t *testing.T) {
	svc := seeded(t)
	item := service.SampleBook(12)
	item.Isbn = ""
	_, err := svc.CreateBook(item)
	wantField(t, err, "isbn")
}

func TestBookRejectsBadPages(t *testing.T) {
	svc := seeded(t)
	item := service.SampleBook(12)
	item.Pages = -1
	_, err := svc.CreateBook(item)
	wantField(t, err, "pages")
}

func TestBookRejectsBadPrice(t *testing.T) {
	svc := seeded(t)
	item := service.SampleBook(12)
	item.Price = -5
	_, err := svc.CreateBook(item)
	wantField(t, err, "price")
}

func TestBookRejectsBadPublished(t *testing.T) {
	svc := seeded(t)
	item := service.SampleBook(12)
	item.Published = "2026-02-30"
	_, err := svc.CreateBook(item)
	wantField(t, err, "published")
}

func TestBookRejectsBadGenre(t *testing.T) {
	svc := seeded(t)
	item := service.SampleBook(12)
	item.Genre = "nope"
	_, err := svc.CreateBook(item)
	wantField(t, err, "genre")
}

func TestBookAuthorIDMustExist(t *testing.T) {
	svc := seeded(t)
	item := service.SampleBook(13)
	item.AuthorID = 9999
	if _, err := svc.CreateBook(item); !errors.Is(err, service.ErrNotFound) {
		t.Fatalf("want ErrNotFound, got %v", err)
	}
}
