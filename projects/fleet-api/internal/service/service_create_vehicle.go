package service

import "fleet-api/internal/model"

// CreateVehicle validates and stores a new vehicle.
func (s *Service) CreateVehicle(item model.Vehicle) (model.Vehicle, error) {
	item.ID = 0
	if err := item.Validate(); err != nil {
		return model.Vehicle{}, err
	}
	if err := s.checkVehicleLinks(item); err != nil {
		return model.Vehicle{}, err
	}
	return s.Vehicles.Create(item), nil
}

// GetVehicle returns one vehicle.
func (s *Service) GetVehicle(id int) (model.Vehicle, error) {
	item, ok := s.Vehicles.Get(id)
	if !ok {
		return model.Vehicle{}, notFound("vehicle", id)
	}
	return item, nil
}

// ListVehicles returns every vehicle, oldest first.
func (s *Service) ListVehicles() []model.Vehicle {
	return s.Vehicles.List()
}
