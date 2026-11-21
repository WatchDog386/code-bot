package shortener

import (
	"errors"
	"testing"
	"time"

	"github.com/example/link-shortener/internal/store"
)

func TestShortenAndResolve(t *testing.T) {
	svc := New(store.NewMemoryStore(), 7)

	link, err := svc.Shorten("https://example.com/docs", 0)
	if err != nil {
		t.Fatalf("shorten: %v", err)
	}
	if len(link.Code) != 7 {
		t.Errorf("expected code length 7, got %d", len(link.Code))
	}

	target, err := svc.Resolve(link.Code)
	if err != nil {
		t.Fatalf("resolve: %v", err)
	}
	if target != "https://example.com/docs" {
		t.Errorf("unexpected target %q", target)
	}
}

func TestRejectsInvalidURL(t *testing.T) {
	svc := New(store.NewMemoryStore(), 6)
	for _, raw := range []string{"", "not a url", "ftp://files.example.com"} {
		if _, err := svc.Shorten(raw, 0); !errors.Is(err, ErrInvalidURL) {
			t.Errorf("%q: expected ErrInvalidURL, got %v", raw, err)
		}
	}
}

func TestExpiredLink(t *testing.T) {
	svc := New(store.NewMemoryStore(), 6)
	start := time.Date(2025, 1, 1, 12, 0, 0, 0, time.UTC)
	svc.now = func() time.Time { return start }

	link, err := svc.Shorten("https://example.com", time.Hour)
	if err != nil {
		t.Fatal(err)
	}

	svc.now = func() time.Time { return start.Add(2 * time.Hour) }
	if _, err := svc.Resolve(link.Code); !errors.Is(err, store.ErrNotFound) {
		t.Errorf("expected expired link to be not found, got %v", err)
	}
}
