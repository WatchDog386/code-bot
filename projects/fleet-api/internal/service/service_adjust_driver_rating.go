package service

import (
	"math"

	"fleet-api/internal/model"
)

// AdjustDriverRating adds delta to the rating of a driver (it can't go below zero).
func (s *Service) AdjustDriverRating(id int, delta float64) (model.Driver, error) {
	item, err := s.GetDriver(id)
	if err != nil {
		return model.Driver{}, err
	}
	value := math.Round((item.Rating+delta)*100) / 100
	return s.UpdateDriver(id, model.DriverPatch{Rating: &value})
}

// ToggleDriverOnDuty flips the on duty flag of a driver.
func (s *Service) ToggleDriverOnDuty(id int) (model.Driver, error) {
	item, err := s.GetDriver(id)
	if err != nil {
		return model.Driver{}, err
	}
	flipped := !item.OnDuty
	return s.UpdateDriver(id, model.DriverPatch{OnDuty: &flipped})
}

// DriverStats sums up every driver.
type DriverStats struct {
	Count         int     `json:"count"`
	TotalRating   float64 `json:"total_rating"`
	AverageRating float64 `json:"average_rating"`
	OnDuty        int     `json:"on_duty"`
}

// DriverStats returns totals and breakdowns over every driver.
func (s *Service) DriverStats() DriverStats {
	return DriverStats{
		Count:         s.Drivers.Count(),
		TotalRating:   s.Drivers.TotalRating(),
		AverageRating: s.Drivers.AverageRating(),
		OnDuty:        len(s.Drivers.WhereOnDuty(true)),
	}
}
