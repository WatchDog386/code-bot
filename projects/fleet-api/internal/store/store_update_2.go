package store

import "fleet-api/internal/model"

// Update replaces an existing record; false if there is none.
func (s *IncidentStore) Update(item model.Incident) bool {
	s.mu.Lock()
	defer s.mu.Unlock()
	if _, ok := s.items[item.ID]; !ok {
		return false
	}
	s.items[item.ID] = item
	return true
}

// Delete removes a record; false if there was none.
func (s *IncidentStore) Delete(id int) bool {
	s.mu.Lock()
	defer s.mu.Unlock()
	if _, ok := s.items[id]; !ok {
		return false
	}
	delete(s.items, id)
	return true
}

// Count is the number of records.
func (s *IncidentStore) Count() int {
	s.mu.RLock()
	defer s.mu.RUnlock()
	return len(s.items)
}

// Filter returns the records keep() accepts, oldest first.
func (s *IncidentStore) Filter(keep func(model.Incident) bool) []model.Incident {
	out := []model.Incident{}
	for _, item := range s.List() {
		if keep(item) {
			out = append(out, item)
		}
	}
	return out
}

// ForVehicle returns records linked to vehicle id.
func (s *IncidentStore) ForVehicle(id int) []model.Incident {
	return s.Filter(func(item model.Incident) bool { return item.VehicleID == id })
}

// CountForVehicle counts records linked to vehicle id.
func (s *IncidentStore) CountForVehicle(id int) int {
	return len(s.ForVehicle(id))
}

// ForDriver returns records linked to driver id.
func (s *IncidentStore) ForDriver(id int) []model.Incident {
	return s.Filter(func(item model.Incident) bool { return item.DriverID == id })
}

// CountForDriver counts records linked to driver id.
func (s *IncidentStore) CountForDriver(id int) int {
	return len(s.ForDriver(id))
}

// HappenedBefore returns records whose happened is before day (YYYY-MM-DD).
func (s *IncidentStore) HappenedBefore(day string) []model.Incident {
	return s.Filter(func(item model.Incident) bool { return item.Happened < day })
}
