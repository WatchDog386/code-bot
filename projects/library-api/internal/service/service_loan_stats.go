package service

import (
	"fmt"
	"math"

	"library-api/internal/model"
)

// LoanStats sums up every loan.
type LoanStats struct {
	Count           int                      `json:"count"`
	TotalRenewals   int                      `json:"total_renewals"`
	AverageRenewals float64                  `json:"average_renewals"`
	ByStatus        map[model.LoanStatus]int `json:"by_status"`
	TotalFee        float64                  `json:"total_fee"`
	AverageFee      float64                  `json:"average_fee"`
}

// LoanStats returns totals and breakdowns over every loan.
func (s *Service) LoanStats() LoanStats {
	return LoanStats{
		Count:           s.Loans.Count(),
		TotalRenewals:   s.Loans.TotalRenewals(),
		AverageRenewals: s.Loans.AverageRenewals(),
		ByStatus:        s.Loans.CountByStatus(),
		TotalFee:        s.Loans.TotalFee(),
		AverageFee:      s.Loans.AverageFee(),
	}
}

// SampleLoan returns valid data for a new loan (links point at seeded records).
func SampleLoan(i int) model.Loan {
	return model.Loan{
		BookID:   (i-1)%3 + 1,
		MemberID: (i-1)%3 + 1,
		Borrowed: fmt.Sprintf("2026-%02d-%02d", i%12+1, i%28+1),
		Due:      fmt.Sprintf("2026-%02d-%02d", i%12+1, i%28+1),
		Renewals: i + 1,
		Status:   model.LoanStatusValues[i%4],
		Fee:      math.Round((10*float64(i)+0.99)*100) / 100,
	}
}

// CreateReservation validates and stores a new reservation.
func (s *Service) CreateReservation(item model.Reservation) (model.Reservation, error) {
	item.ID = 0
	if err := item.Validate(); err != nil {
		return model.Reservation{}, err
	}
	if err := s.checkReservationLinks(item); err != nil {
		return model.Reservation{}, err
	}
	return s.Reservations.Create(item), nil
}

// GetReservation returns one reservation.
func (s *Service) GetReservation(id int) (model.Reservation, error) {
	item, ok := s.Reservations.Get(id)
	if !ok {
		return model.Reservation{}, notFound("reservation", id)
	}
	return item, nil
}
