package store

import "warehouse-api/internal/model"

// MaxExpected returns the record with the highest expected.
func (s *StockCountStore) MaxExpected() (model.StockCount, bool) {
	var best model.StockCount
	found := false
	for _, item := range s.List() {
		if !found || item.Expected > best.Expected {
			best, found = item, true
		}
	}
	return best, found
}

// BetweenFound returns records whose found is within [low, high].
func (s *StockCountStore) BetweenFound(low, high int) []model.StockCount {
	return s.Filter(func(item model.StockCount) bool { return item.Found >= low && item.Found <= high })
}

// TotalFound adds up the found of every record.
func (s *StockCountStore) TotalFound() int {
	var total int
	for _, item := range s.List() {
		total += item.Found
	}
	return total
}

// AverageFound is the mean found (0 when there are no records).
func (s *StockCountStore) AverageFound() float64 {
	items := s.List()
	if len(items) == 0 {
		return 0
	}
	return float64(s.TotalFound()) / float64(len(items))
}
