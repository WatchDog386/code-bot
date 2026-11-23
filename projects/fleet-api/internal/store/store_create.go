package store

import (
	"sort"

	"fleet-api/internal/model"
)

// Create stores item under the next id and returns it.
func (s *FuelLogStore) Create(item model.FuelLog) model.FuelLog {
	s.mu.Lock()
	defer s.mu.Unlock()
	item.ID = s.nextID
	s.nextID++
	s.items[item.ID] = item
	return item
}

// Get returns the record with that id.
func (s *FuelLogStore) Get(id int) (model.FuelLog, bool) {
	s.mu.RLock()
	defer s.mu.RUnlock()
	item, ok := s.items[id]
	return item, ok
}

// List returns every record, oldest first.
func (s *FuelLogStore) List() []model.FuelLog {
	s.mu.RLock()
	defer s.mu.RUnlock()
	out := make([]model.FuelLog, 0, len(s.items))
	for _, item := range s.items {
		out = append(out, item)
	}
	sort.Slice(out, func(i, j int) bool { return out[i].ID < out[j].ID })
	return out
}

// Update replaces an existing record; false if there is none.
func (s *FuelLogStore) Update(item model.FuelLog) bool {
	s.mu.Lock()
	defer s.mu.Unlock()
	if _, ok := s.items[item.ID]; !ok {
		return false
	}
	s.items[item.ID] = item
	return true
}

// Delete removes a record; false if there was none.
func (s *FuelLogStore) Delete(id int) bool {
	s.mu.Lock()
	defer s.mu.Unlock()
	if _, ok := s.items[id]; !ok {
		return false
	}
	delete(s.items, id)
	return true
}

// Count is the number of records.
func (s *FuelLogStore) Count() int {
	s.mu.RLock()
	defer s.mu.RUnlock()
	return len(s.items)
}

// Filter returns the records keep() accepts, oldest first.
func (s *FuelLogStore) Filter(keep func(model.FuelLog) bool) []model.FuelLog {
	out := []model.FuelLog{}
	for _, item := range s.List() {
		if keep(item) {
			out = append(out, item)
		}
	}
	return out
}

// ForVehicle returns records linked to vehicle id.
func (s *FuelLogStore) ForVehicle(id int) []model.FuelLog {
	return s.Filter(func(item model.FuelLog) bool { return item.VehicleID == id })
}

// CountForVehicle counts records linked to vehicle id.
func (s *FuelLogStore) CountForVehicle(id int) int {
	return len(s.ForVehicle(id))
}

// FilledBefore returns records whose filled is before day (YYYY-MM-DD).
func (s *FuelLogStore) FilledBefore(day string) []model.FuelLog {
	return s.Filter(func(item model.FuelLog) bool { return item.Filled < day })
}

// FilledAfter returns records whose filled is after day (YYYY-MM-DD).
func (s *FuelLogStore) FilledAfter(day string) []model.FuelLog {
	return s.Filter(func(item model.FuelLog) bool { return item.Filled > day })
}
