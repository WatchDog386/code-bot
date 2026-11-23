package service

import (
	"fmt"
	"math"

	"fleet-api/internal/model"
)

// UpdateTrip applies patch to a trip.
func (s *Service) UpdateTrip(id int, patch model.TripPatch) (model.Trip, error) {
	current, err := s.GetTrip(id)
	if err != nil {
		return model.Trip{}, err
	}
	updated, err := patch.Apply(current)
	if err != nil {
		return model.Trip{}, err
	}
	if err := s.checkTripLinks(updated); err != nil {
		return model.Trip{}, err
	}
	s.Trips.Update(updated)
	return updated, nil
}

// DeleteTrip removes a trip nothing points at any more.
func (s *Service) DeleteTrip(id int) error {
	if _, err := s.GetTrip(id); err != nil {
		return err
	}
	s.Trips.Delete(id)
	return nil
}

// checkTripLinks makes sure every record a trip points at exists.
func (s *Service) checkTripLinks(item model.Trip) error {
	if _, ok := s.Vehicles.Get(item.VehicleID); !ok {
		return notFound("vehicle", item.VehicleID)
	}
	if _, ok := s.Drivers.Get(item.DriverID); !ok {
		return notFound("driver", item.DriverID)
	}
	return nil
}

// AdjustTripDistanceKm adds delta to the distance km of a trip (it can't go below zero).
func (s *Service) AdjustTripDistanceKm(id int, delta float64) (model.Trip, error) {
	item, err := s.GetTrip(id)
	if err != nil {
		return model.Trip{}, err
	}
	value := math.Round((item.DistanceKm+delta)*100) / 100
	return s.UpdateTrip(id, model.TripPatch{DistanceKm: &value})
}

// SetTripStatus moves a trip to another status.
func (s *Service) SetTripStatus(id int, value model.TripStatus) (model.Trip, error) {
	return s.UpdateTrip(id, model.TripPatch{Status: &value})
}

// TripStats sums up every trip.
type TripStats struct {
	Count             int                      `json:"count"`
	TotalDistanceKm   float64                  `json:"total_distance_km"`
	AverageDistanceKm float64                  `json:"average_distance_km"`
	ByStatus          map[model.TripStatus]int `json:"by_status"`
}

// TripStats returns totals and breakdowns over every trip.
func (s *Service) TripStats() TripStats {
	return TripStats{
		Count:             s.Trips.Count(),
		TotalDistanceKm:   s.Trips.TotalDistanceKm(),
		AverageDistanceKm: s.Trips.AverageDistanceKm(),
		ByStatus:          s.Trips.CountByStatus(),
	}
}

// SampleTrip returns valid data for a new trip (links point at seeded records).
func SampleTrip(i int) model.Trip {
	return model.Trip{
		VehicleID:  (i-1)%3 + 1,
		DriverID:   (i-1)%3 + 1,
		Started:    fmt.Sprintf("2026-%02d-%02d", i%12+1, i%28+1),
		DistanceKm: 1.5*float64(i) + 0.25,
		Purpose:    fmt.Sprintf("Trip purpose %d", i),
		Status:     model.TripStatusValues[i%4],
	}
}
