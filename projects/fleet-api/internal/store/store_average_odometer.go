package store

import "fleet-api/internal/model"

// AverageOdometer is the mean odometer (0 when there are no records).
func (s *ServiceRecordStore) AverageOdometer() float64 {
	items := s.List()
	if len(items) == 0 {
		return 0
	}
	return float64(s.TotalOdometer()) / float64(len(items))
}

// MaxOdometer returns the record with the highest odometer.
func (s *ServiceRecordStore) MaxOdometer() (model.ServiceRecord, bool) {
	var best model.ServiceRecord
	found := false
	for _, item := range s.List() {
		if !found || item.Odometer > best.Odometer {
			best, found = item, true
		}
	}
	return best, found
}

// BetweenCost returns records whose cost is within [low, high].
func (s *ServiceRecordStore) BetweenCost(low, high float64) []model.ServiceRecord {
	return s.Filter(func(item model.ServiceRecord) bool { return item.Cost >= low && item.Cost <= high })
}

// TotalCost adds up the cost of every record.
func (s *ServiceRecordStore) TotalCost() float64 {
	var total float64
	for _, item := range s.List() {
		total += item.Cost
	}
	return total
}

// AverageCost is the mean cost (0 when there are no records).
func (s *ServiceRecordStore) AverageCost() float64 {
	items := s.List()
	if len(items) == 0 {
		return 0
	}
	return float64(s.TotalCost()) / float64(len(items))
}
