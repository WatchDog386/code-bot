package service

import (
	"math"

	"fleet-api/internal/model"
)

// CreateFuelLog validates and stores a new fuel log.
func (s *Service) CreateFuelLog(item model.FuelLog) (model.FuelLog, error) {
	item.ID = 0
	if err := item.Validate(); err != nil {
		return model.FuelLog{}, err
	}
	if err := s.checkFuelLogLinks(item); err != nil {
		return model.FuelLog{}, err
	}
	return s.FuelLogs.Create(item), nil
}

// GetFuelLog returns one fuel log.
func (s *Service) GetFuelLog(id int) (model.FuelLog, error) {
	item, ok := s.FuelLogs.Get(id)
	if !ok {
		return model.FuelLog{}, notFound("fuel log", id)
	}
	return item, nil
}

// ListFuelLogs returns every fuel log, oldest first.
func (s *Service) ListFuelLogs() []model.FuelLog {
	return s.FuelLogs.List()
}

// UpdateFuelLog applies patch to a fuel log.
func (s *Service) UpdateFuelLog(id int, patch model.FuelLogPatch) (model.FuelLog, error) {
	current, err := s.GetFuelLog(id)
	if err != nil {
		return model.FuelLog{}, err
	}
	updated, err := patch.Apply(current)
	if err != nil {
		return model.FuelLog{}, err
	}
	if err := s.checkFuelLogLinks(updated); err != nil {
		return model.FuelLog{}, err
	}
	s.FuelLogs.Update(updated)
	return updated, nil
}

// DeleteFuelLog removes a fuel log nothing points at any more.
func (s *Service) DeleteFuelLog(id int) error {
	if _, err := s.GetFuelLog(id); err != nil {
		return err
	}
	s.FuelLogs.Delete(id)
	return nil
}

// checkFuelLogLinks makes sure every record a fuel log points at exists.
func (s *Service) checkFuelLogLinks(item model.FuelLog) error {
	if _, ok := s.Vehicles.Get(item.VehicleID); !ok {
		return notFound("vehicle", item.VehicleID)
	}
	return nil
}

// AdjustFuelLogLitres adds delta to the litres of a fuel log (it can't go below zero).
func (s *Service) AdjustFuelLogLitres(id int, delta float64) (model.FuelLog, error) {
	item, err := s.GetFuelLog(id)
	if err != nil {
		return model.FuelLog{}, err
	}
	value := math.Round((item.Litres+delta)*100) / 100
	return s.UpdateFuelLog(id, model.FuelLogPatch{Litres: &value})
}
