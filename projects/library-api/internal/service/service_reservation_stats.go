package service

import (
	"fmt"

	"library-api/internal/model"
)

// ReservationStats sums up every reservation.
type ReservationStats struct {
	Count           int                             `json:"count"`
	TotalPosition   int                             `json:"total_position"`
	AveragePosition float64                         `json:"average_position"`
	ByStatus        map[model.ReservationStatus]int `json:"by_status"`
}

// ReservationStats returns totals and breakdowns over every reservation.
func (s *Service) ReservationStats() ReservationStats {
	return ReservationStats{
		Count:           s.Reservations.Count(),
		TotalPosition:   s.Reservations.TotalPosition(),
		AveragePosition: s.Reservations.AveragePosition(),
		ByStatus:        s.Reservations.CountByStatus(),
	}
}

// SampleReservation returns valid data for a new reservation (links point at seeded records).
func SampleReservation(i int) model.Reservation {
	return model.Reservation{
		BookID:    (i-1)%3 + 1,
		MemberID:  (i-1)%3 + 1,
		Requested: fmt.Sprintf("2026-%02d-%02d", i%12+1, i%28+1),
		Position:  i + 1,
		Status:    model.ReservationStatusValues[i%4],
		Notes:     fmt.Sprintf("Notes about reservation %d.", i),
	}
}

// CreateBranch validates and stores a new branch.
func (s *Service) CreateBranch(item model.Branch) (model.Branch, error) {
	item.ID = 0
	if err := item.Validate(); err != nil {
		return model.Branch{}, err
	}
	if err := s.checkBranchLinks(item); err != nil {
		return model.Branch{}, err
	}
	return s.Branches.Create(item), nil
}

// GetBranch returns one branch.
func (s *Service) GetBranch(id int) (model.Branch, error) {
	item, ok := s.Branches.Get(id)
	if !ok {
		return model.Branch{}, notFound("branch", id)
	}
	return item, nil
}

// ListBranches returns every branch, oldest first.
func (s *Service) ListBranches() []model.Branch {
	return s.Branches.List()
}
