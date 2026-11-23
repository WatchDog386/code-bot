package service_test

import (
	"errors"
	"testing"

	"library-api/internal/model"
	"library-api/internal/service"
)

func TestSetBookGenre(t *testing.T) {
	svc := seeded(t)
	last := model.BookGenreValues[len(model.BookGenreValues)-1]
	item, err := svc.SetBookGenre(1, last)
	if err != nil || item.Genre != last {
		t.Fatalf("set = %v, %v", item.Genre, err)
	}
	if got, want := svc.Books.CountByGenre()[last], len(svc.Books.WithGenre(last)); got != want {
		t.Fatalf("count %d != %d", got, want)
	}
}

func TestToggleBookAvailable(t *testing.T) {
	svc := seeded(t)
	before, _ := svc.GetBook(1)
	after, err := svc.ToggleBookAvailable(1)
	if err != nil || after.Available == before.Available {
		t.Fatalf("toggle = %v, %v", after.Available, err)
	}
}

func TestDeleteBook(t *testing.T) {
	svc := seeded(t)
	item, err := svc.CreateBook(service.SampleBook(14))
	if err != nil {
		t.Fatalf("create: %v", err)
	}
	if err := svc.DeleteBook(item.ID); err != nil {
		t.Fatalf("delete: %v", err)
	}
	if _, err := svc.GetBook(item.ID); !errors.Is(err, service.ErrNotFound) {
		t.Fatalf("still there: %v", err)
	}
}

func TestDeleteBookInUse(t *testing.T) {
	svc := seeded(t)
	if err := svc.DeleteBook(1); !errors.Is(err, service.ErrConflict) {
		t.Fatalf("want ErrConflict, got %v", err)
	}
}

func TestBookStats(t *testing.T) {
	svc := seeded(t)
	if got := svc.BookStats().Count; got != 3 {
		t.Fatalf("count = %d", got)
	}
}
