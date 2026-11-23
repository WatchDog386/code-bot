package store

import "library-api/internal/model"

// CountForBook counts records linked to book id.
func (s *ReservationStore) CountForBook(id int) int {
	return len(s.ForBook(id))
}

// ForMember returns records linked to member id.
func (s *ReservationStore) ForMember(id int) []model.Reservation {
	return s.Filter(func(item model.Reservation) bool { return item.MemberID == id })
}

// CountForMember counts records linked to member id.
func (s *ReservationStore) CountForMember(id int) int {
	return len(s.ForMember(id))
}

// RequestedBefore returns records whose requested is before day (YYYY-MM-DD).
func (s *ReservationStore) RequestedBefore(day string) []model.Reservation {
	return s.Filter(func(item model.Reservation) bool { return item.Requested < day })
}

// RequestedAfter returns records whose requested is after day (YYYY-MM-DD).
func (s *ReservationStore) RequestedAfter(day string) []model.Reservation {
	return s.Filter(func(item model.Reservation) bool { return item.Requested > day })
}

// RequestedOn returns records whose requested is day.
func (s *ReservationStore) RequestedOn(day string) []model.Reservation {
	return s.Filter(func(item model.Reservation) bool { return item.Requested == day })
}

// BetweenPosition returns records whose position is within [low, high].
func (s *ReservationStore) BetweenPosition(low, high int) []model.Reservation {
	return s.Filter(func(item model.Reservation) bool { return item.Position >= low && item.Position <= high })
}

// TotalPosition adds up the position of every record.
func (s *ReservationStore) TotalPosition() int {
	var total int
	for _, item := range s.List() {
		total += item.Position
	}
	return total
}
