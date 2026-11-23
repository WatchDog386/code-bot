package store

import "fleet-api/internal/model"

// MaxYear returns the record with the highest year.
func (s *VehicleStore) MaxYear() (model.Vehicle, bool) {
	var best model.Vehicle
	found := false
	for _, item := range s.List() {
		if !found || item.Year > best.Year {
			best, found = item, true
		}
	}
	return best, found
}

// BetweenMileage returns records whose mileage is within [low, high].
func (s *VehicleStore) BetweenMileage(low, high int) []model.Vehicle {
	return s.Filter(func(item model.Vehicle) bool { return item.Mileage >= low && item.Mileage <= high })
}

// TotalMileage adds up the mileage of every record.
func (s *VehicleStore) TotalMileage() int {
	var total int
	for _, item := range s.List() {
		total += item.Mileage
	}
	return total
}

// AverageMileage is the mean mileage (0 when there are no records).
func (s *VehicleStore) AverageMileage() float64 {
	items := s.List()
	if len(items) == 0 {
		return 0
	}
	return float64(s.TotalMileage()) / float64(len(items))
}
