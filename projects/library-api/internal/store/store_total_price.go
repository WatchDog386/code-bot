package store

import "library-api/internal/model"

// TotalPrice adds up the price of every record.
func (s *BookStore) TotalPrice() float64 {
	var total float64
	for _, item := range s.List() {
		total += item.Price
	}
	return total
}

// AveragePrice is the mean price (0 when there are no records).
func (s *BookStore) AveragePrice() float64 {
	items := s.List()
	if len(items) == 0 {
		return 0
	}
	return float64(s.TotalPrice()) / float64(len(items))
}

// MaxPrice returns the record with the highest price.
func (s *BookStore) MaxPrice() (model.Book, bool) {
	var best model.Book
	found := false
	for _, item := range s.List() {
		if !found || item.Price > best.Price {
			best, found = item, true
		}
	}
	return best, found
}

// PublishedBefore returns records whose published is before day (YYYY-MM-DD).
func (s *BookStore) PublishedBefore(day string) []model.Book {
	return s.Filter(func(item model.Book) bool { return item.Published < day })
}

// PublishedAfter returns records whose published is after day (YYYY-MM-DD).
func (s *BookStore) PublishedAfter(day string) []model.Book {
	return s.Filter(func(item model.Book) bool { return item.Published > day })
}

// PublishedOn returns records whose published is day.
func (s *BookStore) PublishedOn(day string) []model.Book {
	return s.Filter(func(item model.Book) bool { return item.Published == day })
}

// WithGenre returns records whose genre is value.
func (s *BookStore) WithGenre(value model.BookGenre) []model.Book {
	return s.Filter(func(item model.Book) bool { return item.Genre == value })
}
