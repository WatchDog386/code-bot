package service

import "library-api/internal/model"

// ListReservations returns every reservation, oldest first.
func (s *Service) ListReservations() []model.Reservation {
	return s.Reservations.List()
}

// UpdateReservation applies patch to a reservation.
func (s *Service) UpdateReservation(id int, patch model.ReservationPatch) (model.Reservation, error) {
	current, err := s.GetReservation(id)
	if err != nil {
		return model.Reservation{}, err
	}
	updated, err := patch.Apply(current)
	if err != nil {
		return model.Reservation{}, err
	}
	if err := s.checkReservationLinks(updated); err != nil {
		return model.Reservation{}, err
	}
	s.Reservations.Update(updated)
	return updated, nil
}

// DeleteReservation removes a reservation nothing points at any more.
func (s *Service) DeleteReservation(id int) error {
	if _, err := s.GetReservation(id); err != nil {
		return err
	}
	s.Reservations.Delete(id)
	return nil
}
