package service

import "fleet-api/internal/model"

// CreateIncident validates and stores a new incident.
func (s *Service) CreateIncident(item model.Incident) (model.Incident, error) {
	item.ID = 0
	if err := item.Validate(); err != nil {
		return model.Incident{}, err
	}
	if err := s.checkIncidentLinks(item); err != nil {
		return model.Incident{}, err
	}
	return s.Incidents.Create(item), nil
}

// GetIncident returns one incident.
func (s *Service) GetIncident(id int) (model.Incident, error) {
	item, ok := s.Incidents.Get(id)
	if !ok {
		return model.Incident{}, notFound("incident", id)
	}
	return item, nil
}

// ListIncidents returns every incident, oldest first.
func (s *Service) ListIncidents() []model.Incident {
	return s.Incidents.List()
}

// UpdateIncident applies patch to a incident.
func (s *Service) UpdateIncident(id int, patch model.IncidentPatch) (model.Incident, error) {
	current, err := s.GetIncident(id)
	if err != nil {
		return model.Incident{}, err
	}
	updated, err := patch.Apply(current)
	if err != nil {
		return model.Incident{}, err
	}
	if err := s.checkIncidentLinks(updated); err != nil {
		return model.Incident{}, err
	}
	s.Incidents.Update(updated)
	return updated, nil
}

// DeleteIncident removes a incident nothing points at any more.
func (s *Service) DeleteIncident(id int) error {
	if _, err := s.GetIncident(id); err != nil {
		return err
	}
	s.Incidents.Delete(id)
	return nil
}

// checkIncidentLinks makes sure every record a incident points at exists.
func (s *Service) checkIncidentLinks(item model.Incident) error {
	if _, ok := s.Vehicles.Get(item.VehicleID); !ok {
		return notFound("vehicle", item.VehicleID)
	}
	if _, ok := s.Drivers.Get(item.DriverID); !ok {
		return notFound("driver", item.DriverID)
	}
	return nil
}
