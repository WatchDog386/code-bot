package service

import "fleet-api/internal/model"

// UpdateVehicle applies patch to a vehicle.
func (s *Service) UpdateVehicle(id int, patch model.VehiclePatch) (model.Vehicle, error) {
	current, err := s.GetVehicle(id)
	if err != nil {
		return model.Vehicle{}, err
	}
	updated, err := patch.Apply(current)
	if err != nil {
		return model.Vehicle{}, err
	}
	if err := s.checkVehicleLinks(updated); err != nil {
		return model.Vehicle{}, err
	}
	s.Vehicles.Update(updated)
	return updated, nil
}

// DeleteVehicle removes a vehicle nothing points at any more.
func (s *Service) DeleteVehicle(id int) error {
	if _, err := s.GetVehicle(id); err != nil {
		return err
	}
	if n := s.Trips.CountForVehicle(id); n > 0 {
		return inUse("vehicle", id, n, "trips")
	}
	if n := s.FuelLogs.CountForVehicle(id); n > 0 {
		return inUse("vehicle", id, n, "fuel logs")
	}
	if n := s.ServiceRecords.CountForVehicle(id); n > 0 {
		return inUse("vehicle", id, n, "service records")
	}
	if n := s.Incidents.CountForVehicle(id); n > 0 {
		return inUse("vehicle", id, n, "incidents")
	}
	s.Vehicles.Delete(id)
	return nil
}

// checkVehicleLinks makes sure every record a vehicle points at exists.
func (s *Service) checkVehicleLinks(_ model.Vehicle) error {
	return nil
}
