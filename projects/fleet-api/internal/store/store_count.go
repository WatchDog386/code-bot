package store

import "fleet-api/internal/model"

// Count is the number of records.
func (s *TripStore) Count() int {
	s.mu.RLock()
	defer s.mu.RUnlock()
	return len(s.items)
}

// Filter returns the records keep() accepts, oldest first.
func (s *TripStore) Filter(keep func(model.Trip) bool) []model.Trip {
	out := []model.Trip{}
	for _, item := range s.List() {
		if keep(item) {
			out = append(out, item)
		}
	}
	return out
}

// ForVehicle returns records linked to vehicle id.
func (s *TripStore) ForVehicle(id int) []model.Trip {
	return s.Filter(func(item model.Trip) bool { return item.VehicleID == id })
}

// CountForVehicle counts records linked to vehicle id.
func (s *TripStore) CountForVehicle(id int) int {
	return len(s.ForVehicle(id))
}

// ForDriver returns records linked to driver id.
func (s *TripStore) ForDriver(id int) []model.Trip {
	return s.Filter(func(item model.Trip) bool { return item.DriverID == id })
}

// CountForDriver counts records linked to driver id.
func (s *TripStore) CountForDriver(id int) int {
	return len(s.ForDriver(id))
}

// StartedBefore returns records whose started is before day (YYYY-MM-DD).
func (s *TripStore) StartedBefore(day string) []model.Trip {
	return s.Filter(func(item model.Trip) bool { return item.Started < day })
}

// StartedAfter returns records whose started is after day (YYYY-MM-DD).
func (s *TripStore) StartedAfter(day string) []model.Trip {
	return s.Filter(func(item model.Trip) bool { return item.Started > day })
}

// StartedOn returns records whose started is day.
func (s *TripStore) StartedOn(day string) []model.Trip {
	return s.Filter(func(item model.Trip) bool { return item.Started == day })
}

// BetweenDistanceKm returns records whose distance km is within [low, high].
func (s *TripStore) BetweenDistanceKm(low, high float64) []model.Trip {
	return s.Filter(func(item model.Trip) bool { return item.DistanceKm >= low && item.DistanceKm <= high })
}

// TotalDistanceKm adds up the distance km of every record.
func (s *TripStore) TotalDistanceKm() float64 {
	var total float64
	for _, item := range s.List() {
		total += item.DistanceKm
	}
	return total
}
