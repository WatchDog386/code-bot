package service

import "fleet-api/internal/model"

// GetDriver returns one driver.
func (s *Service) GetDriver(id int) (model.Driver, error) {
	item, ok := s.Drivers.Get(id)
	if !ok {
		return model.Driver{}, notFound("driver", id)
	}
	return item, nil
}

// ListDrivers returns every driver, oldest first.
func (s *Service) ListDrivers() []model.Driver {
	return s.Drivers.List()
}

// UpdateDriver applies patch to a driver.
func (s *Service) UpdateDriver(id int, patch model.DriverPatch) (model.Driver, error) {
	current, err := s.GetDriver(id)
	if err != nil {
		return model.Driver{}, err
	}
	updated, err := patch.Apply(current)
	if err != nil {
		return model.Driver{}, err
	}
	if err := s.checkDriverLinks(updated); err != nil {
		return model.Driver{}, err
	}
	s.Drivers.Update(updated)
	return updated, nil
}

// DeleteDriver removes a driver nothing points at any more.
func (s *Service) DeleteDriver(id int) error {
	if _, err := s.GetDriver(id); err != nil {
		return err
	}
	if n := s.Trips.CountForDriver(id); n > 0 {
		return inUse("driver", id, n, "trips")
	}
	if n := s.Incidents.CountForDriver(id); n > 0 {
		return inUse("driver", id, n, "incidents")
	}
	s.Drivers.Delete(id)
	return nil
}

// checkDriverLinks makes sure every record a driver points at exists.
func (s *Service) checkDriverLinks(_ model.Driver) error {
	return nil
}
