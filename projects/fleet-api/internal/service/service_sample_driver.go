package service

import (
	"fmt"

	"fleet-api/internal/model"
)

// SampleDriver returns valid data for a new driver (links point at seeded records).
func SampleDriver(i int) model.Driver {
	return model.Driver{
		Name:          fmt.Sprintf("Driver name %d", i),
		Email:         fmt.Sprintf("driver%d@example.com", i),
		LicenseNo:     fmt.Sprintf("Driver license no %d", i),
		LicenseExpiry: fmt.Sprintf("2026-%02d-%02d", i%12+1, i%28+1),
		Rating:        1.5*float64(i) + 0.25,
		OnDuty:        i%2 == 1,
	}
}

// CreateTrip validates and stores a new trip.
func (s *Service) CreateTrip(item model.Trip) (model.Trip, error) {
	item.ID = 0
	if err := item.Validate(); err != nil {
		return model.Trip{}, err
	}
	if err := s.checkTripLinks(item); err != nil {
		return model.Trip{}, err
	}
	return s.Trips.Create(item), nil
}

// GetTrip returns one trip.
func (s *Service) GetTrip(id int) (model.Trip, error) {
	item, ok := s.Trips.Get(id)
	if !ok {
		return model.Trip{}, notFound("trip", id)
	}
	return item, nil
}

// ListTrips returns every trip, oldest first.
func (s *Service) ListTrips() []model.Trip {
	return s.Trips.List()
}
