// Package service holds the Fleet Management business rules: validation, links between
// records, small domain operations and statistics.
package service

import (
	"errors"
	"fmt"

	"fleet-api/internal/store"
)

// Errors the service returns (wrapped with details).
var (
	ErrNotFound = errors.New("not found")
	ErrConflict = errors.New("conflict")
)

func notFound(entity string, id int) error {
	return fmt.Errorf("%s %d: %w", entity, id, ErrNotFound)
}

func inUse(entity string, id, n int, by string) error {
	return fmt.Errorf("%s %d is still used by %d %s: %w", entity, id, n, by, ErrConflict)
}

// Service is the whole application: every store plus the rules between them.
type Service struct {
	Vehicles       *store.VehicleStore
	Drivers        *store.DriverStore
	Trips          *store.TripStore
	FuelLogs       *store.FuelLogStore
	ServiceRecords *store.ServiceRecordStore
	Incidents      *store.IncidentStore
}

// New returns a service with empty stores.
func New() *Service {
	return &Service{
		Vehicles:       store.NewVehicleStore(),
		Drivers:        store.NewDriverStore(),
		Trips:          store.NewTripStore(),
		FuelLogs:       store.NewFuelLogStore(),
		ServiceRecords: store.NewServiceRecordStore(),
		Incidents:      store.NewIncidentStore(),
	}
}

// Seed creates n sample records of every kind.
func (s *Service) Seed(n int) error {
	for i := 1; i <= n; i++ {
		if _, err := s.CreateVehicle(SampleVehicle(i)); err != nil {
			return err
		}
		if _, err := s.CreateDriver(SampleDriver(i)); err != nil {
			return err
		}
		if _, err := s.CreateTrip(SampleTrip(i)); err != nil {
			return err
		}
		if _, err := s.CreateFuelLog(SampleFuelLog(i)); err != nil {
			return err
		}
		if _, err := s.CreateServiceRecord(SampleServiceRecord(i)); err != nil {
			return err
		}
		if _, err := s.CreateIncident(SampleIncident(i)); err != nil {
			return err
		}
	}
	return nil
}
