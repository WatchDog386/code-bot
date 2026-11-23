package service

import "library-api/internal/model"

// checkReservationLinks makes sure every record a reservation points at exists.
func (s *Service) checkReservationLinks(item model.Reservation) error {
	if _, ok := s.Books.Get(item.BookID); !ok {
		return notFound("book", item.BookID)
	}
	if _, ok := s.Members.Get(item.MemberID); !ok {
		return notFound("member", item.MemberID)
	}
	return nil
}

// AdjustReservationPosition adds delta to the position of a reservation (it can't go below zero).
func (s *Service) AdjustReservationPosition(id int, delta int) (model.Reservation, error) {
	item, err := s.GetReservation(id)
	if err != nil {
		return model.Reservation{}, err
	}
	value := item.Position + delta
	return s.UpdateReservation(id, model.ReservationPatch{Position: &value})
}

// SetReservationStatus moves a reservation to another status.
func (s *Service) SetReservationStatus(id int, value model.ReservationStatus) (model.Reservation, error) {
	return s.UpdateReservation(id, model.ReservationPatch{Status: &value})
}
