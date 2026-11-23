package store

import (
	"strings"

	"warehouse-api/internal/model"
)

// Count is the number of records.
func (s *BinStore) Count() int {
	s.mu.RLock()
	defer s.mu.RUnlock()
	return len(s.items)
}

// Filter returns the records keep() accepts, oldest first.
func (s *BinStore) Filter(keep func(model.Bin) bool) []model.Bin {
	out := []model.Bin{}
	for _, item := range s.List() {
		if keep(item) {
			out = append(out, item)
		}
	}
	return out
}

// FindByCode returns records whose code is exactly value.
func (s *BinStore) FindByCode(value string) []model.Bin {
	return s.Filter(func(item model.Bin) bool { return item.Code == value })
}

// SearchCode returns records whose code contains text (any case).
func (s *BinStore) SearchCode(text string) []model.Bin {
	needle := strings.ToLower(strings.TrimSpace(text))
	return s.Filter(func(item model.Bin) bool { return strings.Contains(strings.ToLower(item.Code), needle) })
}

// FindByAisle returns records whose aisle is exactly value.
func (s *BinStore) FindByAisle(value string) []model.Bin {
	return s.Filter(func(item model.Bin) bool { return item.Aisle == value })
}

// SearchAisle returns records whose aisle contains text (any case).
func (s *BinStore) SearchAisle(text string) []model.Bin {
	needle := strings.ToLower(strings.TrimSpace(text))
	return s.Filter(func(item model.Bin) bool { return strings.Contains(strings.ToLower(item.Aisle), needle) })
}

// BetweenShelf returns records whose shelf is within [low, high].
func (s *BinStore) BetweenShelf(low, high int) []model.Bin {
	return s.Filter(func(item model.Bin) bool { return item.Shelf >= low && item.Shelf <= high })
}

// TotalShelf adds up the shelf of every record.
func (s *BinStore) TotalShelf() int {
	var total int
	for _, item := range s.List() {
		total += item.Shelf
	}
	return total
}

// AverageShelf is the mean shelf (0 when there are no records).
func (s *BinStore) AverageShelf() float64 {
	items := s.List()
	if len(items) == 0 {
		return 0
	}
	return float64(s.TotalShelf()) / float64(len(items))
}
