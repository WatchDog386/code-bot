package store

import (
	"strings"

	"library-api/internal/model"
)

// FindByEmail returns records whose email is exactly value.
func (s *AuthorStore) FindByEmail(value string) []model.Author {
	return s.Filter(func(item model.Author) bool { return item.Email == value })
}

// SearchEmail returns records whose email contains text (any case).
func (s *AuthorStore) SearchEmail(text string) []model.Author {
	needle := strings.ToLower(strings.TrimSpace(text))
	return s.Filter(func(item model.Author) bool { return strings.Contains(strings.ToLower(item.Email), needle) })
}

// FindByCountry returns records whose country is exactly value.
func (s *AuthorStore) FindByCountry(value string) []model.Author {
	return s.Filter(func(item model.Author) bool { return item.Country == value })
}

// SearchCountry returns records whose country contains text (any case).
func (s *AuthorStore) SearchCountry(text string) []model.Author {
	needle := strings.ToLower(strings.TrimSpace(text))
	return s.Filter(func(item model.Author) bool { return strings.Contains(strings.ToLower(item.Country), needle) })
}

// BornBefore returns records whose born is before day (YYYY-MM-DD).
func (s *AuthorStore) BornBefore(day string) []model.Author {
	return s.Filter(func(item model.Author) bool { return item.Born < day })
}

// BornAfter returns records whose born is after day (YYYY-MM-DD).
func (s *AuthorStore) BornAfter(day string) []model.Author {
	return s.Filter(func(item model.Author) bool { return item.Born > day })
}

// BornOn returns records whose born is day.
func (s *AuthorStore) BornOn(day string) []model.Author {
	return s.Filter(func(item model.Author) bool { return item.Born == day })
}

// WhereActive returns records whose active flag equals flag.
func (s *AuthorStore) WhereActive(flag bool) []model.Author {
	return s.Filter(func(item model.Author) bool { return item.Active == flag })
}
