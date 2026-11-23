package store

import (
	"strings"

	"warehouse-api/internal/model"
)

// MaxFound returns the record with the highest found.
func (s *StockCountStore) MaxFound() (model.StockCount, bool) {
	var best model.StockCount
	found := false
	for _, item := range s.List() {
		if !found || item.Found > best.Found {
			best, found = item, true
		}
	}
	return best, found
}

// FindByCounter returns records whose counter is exactly value.
func (s *StockCountStore) FindByCounter(value string) []model.StockCount {
	return s.Filter(func(item model.StockCount) bool { return item.Counter == value })
}

// SearchCounter returns records whose counter contains text (any case).
func (s *StockCountStore) SearchCounter(text string) []model.StockCount {
	needle := strings.ToLower(strings.TrimSpace(text))
	return s.Filter(func(item model.StockCount) bool { return strings.Contains(strings.ToLower(item.Counter), needle) })
}

// Search returns records where any text field contains text (any case).
func (s *StockCountStore) Search(text string) []model.StockCount {
	needle := strings.ToLower(strings.TrimSpace(text))
	return s.Filter(func(item model.StockCount) bool {
		for _, value := range []string{item.Counter} {
			if strings.Contains(strings.ToLower(value), needle) {
				return true
			}
		}
		return false
	})
}
