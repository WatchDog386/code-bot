package store

import "warehouse-api/internal/model"

// BetweenQuantity returns records whose quantity is within [low, high].
func (s *StockMovementStore) BetweenQuantity(low, high int) []model.StockMovement {
	return s.Filter(func(item model.StockMovement) bool { return item.Quantity >= low && item.Quantity <= high })
}

// TotalQuantity adds up the quantity of every record.
func (s *StockMovementStore) TotalQuantity() int {
	var total int
	for _, item := range s.List() {
		total += item.Quantity
	}
	return total
}

// AverageQuantity is the mean quantity (0 when there are no records).
func (s *StockMovementStore) AverageQuantity() float64 {
	items := s.List()
	if len(items) == 0 {
		return 0
	}
	return float64(s.TotalQuantity()) / float64(len(items))
}

// MaxQuantity returns the record with the highest quantity.
func (s *StockMovementStore) MaxQuantity() (model.StockMovement, bool) {
	var best model.StockMovement
	found := false
	for _, item := range s.List() {
		if !found || item.Quantity > best.Quantity {
			best, found = item, true
		}
	}
	return best, found
}

// MovedBefore returns records whose moved is before day (YYYY-MM-DD).
func (s *StockMovementStore) MovedBefore(day string) []model.StockMovement {
	return s.Filter(func(item model.StockMovement) bool { return item.Moved < day })
}

// MovedAfter returns records whose moved is after day (YYYY-MM-DD).
func (s *StockMovementStore) MovedAfter(day string) []model.StockMovement {
	return s.Filter(func(item model.StockMovement) bool { return item.Moved > day })
}

// MovedOn returns records whose moved is day.
func (s *StockMovementStore) MovedOn(day string) []model.StockMovement {
	return s.Filter(func(item model.StockMovement) bool { return item.Moved == day })
}

// WithReason returns records whose reason is value.
func (s *StockMovementStore) WithReason(value model.StockMovementReason) []model.StockMovement {
	return s.Filter(func(item model.StockMovement) bool { return item.Reason == value })
}

// CountByReason counts records for every reason.
func (s *StockMovementStore) CountByReason() map[model.StockMovementReason]int {
	counts := map[model.StockMovementReason]int{}
	for _, v := range model.StockMovementReasonValues {
		counts[v] = 0
	}
	for _, item := range s.List() {
		counts[item.Reason]++
	}
	return counts
}

// FindByReference returns records whose reference is exactly value.
func (s *StockMovementStore) FindByReference(value string) []model.StockMovement {
	return s.Filter(func(item model.StockMovement) bool { return item.Reference == value })
}
