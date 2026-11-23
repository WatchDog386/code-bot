package store

import "warehouse-api/internal/model"

// ForBin returns records linked to bin id.
func (s *StockCountStore) ForBin(id int) []model.StockCount {
	return s.Filter(func(item model.StockCount) bool { return item.BinID == id })
}

// CountForBin counts records linked to bin id.
func (s *StockCountStore) CountForBin(id int) int {
	return len(s.ForBin(id))
}

// ForProduct returns records linked to product id.
func (s *StockCountStore) ForProduct(id int) []model.StockCount {
	return s.Filter(func(item model.StockCount) bool { return item.ProductID == id })
}

// CountForProduct counts records linked to product id.
func (s *StockCountStore) CountForProduct(id int) int {
	return len(s.ForProduct(id))
}

// CountedBefore returns records whose counted is before day (YYYY-MM-DD).
func (s *StockCountStore) CountedBefore(day string) []model.StockCount {
	return s.Filter(func(item model.StockCount) bool { return item.Counted < day })
}

// CountedAfter returns records whose counted is after day (YYYY-MM-DD).
func (s *StockCountStore) CountedAfter(day string) []model.StockCount {
	return s.Filter(func(item model.StockCount) bool { return item.Counted > day })
}

// CountedOn returns records whose counted is day.
func (s *StockCountStore) CountedOn(day string) []model.StockCount {
	return s.Filter(func(item model.StockCount) bool { return item.Counted == day })
}

// BetweenExpected returns records whose expected is within [low, high].
func (s *StockCountStore) BetweenExpected(low, high int) []model.StockCount {
	return s.Filter(func(item model.StockCount) bool { return item.Expected >= low && item.Expected <= high })
}

// TotalExpected adds up the expected of every record.
func (s *StockCountStore) TotalExpected() int {
	var total int
	for _, item := range s.List() {
		total += item.Expected
	}
	return total
}

// AverageExpected is the mean expected (0 when there are no records).
func (s *StockCountStore) AverageExpected() float64 {
	items := s.List()
	if len(items) == 0 {
		return 0
	}
	return float64(s.TotalExpected()) / float64(len(items))
}
