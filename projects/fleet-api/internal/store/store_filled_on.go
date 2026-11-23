package store

import "fleet-api/internal/model"

// FilledOn returns records whose filled is day.
func (s *FuelLogStore) FilledOn(day string) []model.FuelLog {
	return s.Filter(func(item model.FuelLog) bool { return item.Filled == day })
}

// BetweenLitres returns records whose litres is within [low, high].
func (s *FuelLogStore) BetweenLitres(low, high float64) []model.FuelLog {
	return s.Filter(func(item model.FuelLog) bool { return item.Litres >= low && item.Litres <= high })
}

// TotalLitres adds up the litres of every record.
func (s *FuelLogStore) TotalLitres() float64 {
	var total float64
	for _, item := range s.List() {
		total += item.Litres
	}
	return total
}

// AverageLitres is the mean litres (0 when there are no records).
func (s *FuelLogStore) AverageLitres() float64 {
	items := s.List()
	if len(items) == 0 {
		return 0
	}
	return float64(s.TotalLitres()) / float64(len(items))
}

// MaxLitres returns the record with the highest litres.
func (s *FuelLogStore) MaxLitres() (model.FuelLog, bool) {
	var best model.FuelLog
	found := false
	for _, item := range s.List() {
		if !found || item.Litres > best.Litres {
			best, found = item, true
		}
	}
	return best, found
}

// BetweenCost returns records whose cost is within [low, high].
func (s *FuelLogStore) BetweenCost(low, high float64) []model.FuelLog {
	return s.Filter(func(item model.FuelLog) bool { return item.Cost >= low && item.Cost <= high })
}

// TotalCost adds up the cost of every record.
func (s *FuelLogStore) TotalCost() float64 {
	var total float64
	for _, item := range s.List() {
		total += item.Cost
	}
	return total
}

// AverageCost is the mean cost (0 when there are no records).
func (s *FuelLogStore) AverageCost() float64 {
	items := s.List()
	if len(items) == 0 {
		return 0
	}
	return float64(s.TotalCost()) / float64(len(items))
}

// MaxCost returns the record with the highest cost.
func (s *FuelLogStore) MaxCost() (model.FuelLog, bool) {
	var best model.FuelLog
	found := false
	for _, item := range s.List() {
		if !found || item.Cost > best.Cost {
			best, found = item, true
		}
	}
	return best, found
}
