package store

import "warehouse-api/internal/model"

// TotalUnitPrice adds up the unit price of every record.
func (s *ProductStore) TotalUnitPrice() float64 {
	var total float64
	for _, item := range s.List() {
		total += item.UnitPrice
	}
	return total
}

// AverageUnitPrice is the mean unit price (0 when there are no records).
func (s *ProductStore) AverageUnitPrice() float64 {
	items := s.List()
	if len(items) == 0 {
		return 0
	}
	return float64(s.TotalUnitPrice()) / float64(len(items))
}

// MaxUnitPrice returns the record with the highest unit price.
func (s *ProductStore) MaxUnitPrice() (model.Product, bool) {
	var best model.Product
	found := false
	for _, item := range s.List() {
		if !found || item.UnitPrice > best.UnitPrice {
			best, found = item, true
		}
	}
	return best, found
}

// BetweenReorderLevel returns records whose reorder level is within [low, high].
func (s *ProductStore) BetweenReorderLevel(low, high int) []model.Product {
	return s.Filter(func(item model.Product) bool { return item.ReorderLevel >= low && item.ReorderLevel <= high })
}

// TotalReorderLevel adds up the reorder level of every record.
func (s *ProductStore) TotalReorderLevel() int {
	var total int
	for _, item := range s.List() {
		total += item.ReorderLevel
	}
	return total
}

// AverageReorderLevel is the mean reorder level (0 when there are no records).
func (s *ProductStore) AverageReorderLevel() float64 {
	items := s.List()
	if len(items) == 0 {
		return 0
	}
	return float64(s.TotalReorderLevel()) / float64(len(items))
}
