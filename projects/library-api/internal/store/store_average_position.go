package store

import "library-api/internal/model"

// AveragePosition is the mean position (0 when there are no records).
func (s *ReservationStore) AveragePosition() float64 {
	items := s.List()
	if len(items) == 0 {
		return 0
	}
	return float64(s.TotalPosition()) / float64(len(items))
}

// MaxPosition returns the record with the highest position.
func (s *ReservationStore) MaxPosition() (model.Reservation, bool) {
	var best model.Reservation
	found := false
	for _, item := range s.List() {
		if !found || item.Position > best.Position {
			best, found = item, true
		}
	}
	return best, found
}

// WithStatus returns records whose status is value.
func (s *ReservationStore) WithStatus(value model.ReservationStatus) []model.Reservation {
	return s.Filter(func(item model.Reservation) bool { return item.Status == value })
}

// CountByStatus counts records for every status.
func (s *ReservationStore) CountByStatus() map[model.ReservationStatus]int {
	counts := map[model.ReservationStatus]int{}
	for _, v := range model.ReservationStatusValues {
		counts[v] = 0
	}
	for _, item := range s.List() {
		counts[item.Status]++
	}
	return counts
}
