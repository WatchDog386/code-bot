package store

import (
	"strings"

	"library-api/internal/model"
)

// Filter returns the records keep() accepts, oldest first.
func (s *BookStore) Filter(keep func(model.Book) bool) []model.Book {
	out := []model.Book{}
	for _, item := range s.List() {
		if keep(item) {
			out = append(out, item)
		}
	}
	return out
}

// FindByTitle returns records whose title is exactly value.
func (s *BookStore) FindByTitle(value string) []model.Book {
	return s.Filter(func(item model.Book) bool { return item.Title == value })
}

// SearchTitle returns records whose title contains text (any case).
func (s *BookStore) SearchTitle(text string) []model.Book {
	needle := strings.ToLower(strings.TrimSpace(text))
	return s.Filter(func(item model.Book) bool { return strings.Contains(strings.ToLower(item.Title), needle) })
}

// ForAuthor returns records linked to author id.
func (s *BookStore) ForAuthor(id int) []model.Book {
	return s.Filter(func(item model.Book) bool { return item.AuthorID == id })
}

// CountForAuthor counts records linked to author id.
func (s *BookStore) CountForAuthor(id int) int {
	return len(s.ForAuthor(id))
}

// FindByIsbn returns records whose isbn is exactly value.
func (s *BookStore) FindByIsbn(value string) []model.Book {
	return s.Filter(func(item model.Book) bool { return item.Isbn == value })
}

// SearchIsbn returns records whose isbn contains text (any case).
func (s *BookStore) SearchIsbn(text string) []model.Book {
	needle := strings.ToLower(strings.TrimSpace(text))
	return s.Filter(func(item model.Book) bool { return strings.Contains(strings.ToLower(item.Isbn), needle) })
}

// BetweenPages returns records whose pages is within [low, high].
func (s *BookStore) BetweenPages(low, high int) []model.Book {
	return s.Filter(func(item model.Book) bool { return item.Pages >= low && item.Pages <= high })
}

// TotalPages adds up the pages of every record.
func (s *BookStore) TotalPages() int {
	var total int
	for _, item := range s.List() {
		total += item.Pages
	}
	return total
}

// AveragePages is the mean pages (0 when there are no records).
func (s *BookStore) AveragePages() float64 {
	items := s.List()
	if len(items) == 0 {
		return 0
	}
	return float64(s.TotalPages()) / float64(len(items))
}

// MaxPages returns the record with the highest pages.
func (s *BookStore) MaxPages() (model.Book, bool) {
	var best model.Book
	found := false
	for _, item := range s.List() {
		if !found || item.Pages > best.Pages {
			best, found = item, true
		}
	}
	return best, found
}

// BetweenPrice returns records whose price is within [low, high].
func (s *BookStore) BetweenPrice(low, high float64) []model.Book {
	return s.Filter(func(item model.Book) bool { return item.Price >= low && item.Price <= high })
}
