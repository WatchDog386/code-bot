package service

import (
	"fmt"

	"fleet-api/internal/model"
)

// AdjustVehicleYear adds delta to the year of a vehicle (it can't go below zero).
func (s *Service) AdjustVehicleYear(id int, delta int) (model.Vehicle, error) {
	item, err := s.GetVehicle(id)
	if err != nil {
		return model.Vehicle{}, err
	}
	value := item.Year + delta
	return s.UpdateVehicle(id, model.VehiclePatch{Year: &value})
}

// AdjustVehicleMileage adds delta to the mileage of a vehicle (it can't go below zero).
func (s *Service) AdjustVehicleMileage(id int, delta int) (model.Vehicle, error) {
	item, err := s.GetVehicle(id)
	if err != nil {
		return model.Vehicle{}, err
	}
	value := item.Mileage + delta
	return s.UpdateVehicle(id, model.VehiclePatch{Mileage: &value})
}

// SetVehicleFuel moves a vehicle to another fuel.
func (s *Service) SetVehicleFuel(id int, value model.VehicleFuel) (model.Vehicle, error) {
	return s.UpdateVehicle(id, model.VehiclePatch{Fuel: &value})
}

// ToggleVehicleActive flips the active flag of a vehicle.
func (s *Service) ToggleVehicleActive(id int) (model.Vehicle, error) {
	item, err := s.GetVehicle(id)
	if err != nil {
		return model.Vehicle{}, err
	}
	flipped := !item.Active
	return s.UpdateVehicle(id, model.VehiclePatch{Active: &flipped})
}

// VehicleStats sums up every vehicle.
type VehicleStats struct {
	Count          int                       `json:"count"`
	TotalYear      int                       `json:"total_year"`
	AverageYear    float64                   `json:"average_year"`
	TotalMileage   int                       `json:"total_mileage"`
	AverageMileage float64                   `json:"average_mileage"`
	ByFuel         map[model.VehicleFuel]int `json:"by_fuel"`
	Active         int                       `json:"active"`
}

// VehicleStats returns totals and breakdowns over every vehicle.
func (s *Service) VehicleStats() VehicleStats {
	return VehicleStats{
		Count:          s.Vehicles.Count(),
		TotalYear:      s.Vehicles.TotalYear(),
		AverageYear:    s.Vehicles.AverageYear(),
		TotalMileage:   s.Vehicles.TotalMileage(),
		AverageMileage: s.Vehicles.AverageMileage(),
		ByFuel:         s.Vehicles.CountByFuel(),
		Active:         len(s.Vehicles.WhereActive(true)),
	}
}

// SampleVehicle returns valid data for a new vehicle (links point at seeded records).
func SampleVehicle(i int) model.Vehicle {
	return model.Vehicle{
		Plate:   fmt.Sprintf("Vehicle plate %d", i),
		Make:    fmt.Sprintf("Vehicle make %d", i),
		Model:   fmt.Sprintf("Vehicle model %d", i),
		Year:    i + 1,
		Mileage: i + 1,
		Fuel:    model.VehicleFuelValues[i%4],
		Active:  i%2 == 1,
	}
}

// CreateDriver validates and stores a new driver.
func (s *Service) CreateDriver(item model.Driver) (model.Driver, error) {
	item.ID = 0
	if err := item.Validate(); err != nil {
		return model.Driver{}, err
	}
	if err := s.checkDriverLinks(item); err != nil {
		return model.Driver{}, err
	}
	return s.Drivers.Create(item), nil
}
