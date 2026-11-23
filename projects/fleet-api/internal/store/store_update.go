package store

import (
	"strings"

	"fleet-api/internal/model"
)

// Update replaces an existing record; false if there is none.
func (s *VehicleStore) Update(item model.Vehicle) bool {
	s.mu.Lock()
	defer s.mu.Unlock()
	if _, ok := s.items[item.ID]; !ok {
		return false
	}
	s.items[item.ID] = item
	return true
}

// Delete removes a record; false if there was none.
func (s *VehicleStore) Delete(id int) bool {
	s.mu.Lock()
	defer s.mu.Unlock()
	if _, ok := s.items[id]; !ok {
		return false
	}
	delete(s.items, id)
	return true
}

// Count is the number of records.
func (s *VehicleStore) Count() int {
	s.mu.RLock()
	defer s.mu.RUnlock()
	return len(s.items)
}

// Filter returns the records keep() accepts, oldest first.
func (s *VehicleStore) Filter(keep func(model.Vehicle) bool) []model.Vehicle {
	out := []model.Vehicle{}
	for _, item := range s.List() {
		if keep(item) {
			out = append(out, item)
		}
	}
	return out
}

// FindByPlate returns records whose plate is exactly value.
func (s *VehicleStore) FindByPlate(value string) []model.Vehicle {
	return s.Filter(func(item model.Vehicle) bool { return item.Plate == value })
}

// SearchPlate returns records whose plate contains text (any case).
func (s *VehicleStore) SearchPlate(text string) []model.Vehicle {
	needle := strings.ToLower(strings.TrimSpace(text))
	return s.Filter(func(item model.Vehicle) bool { return strings.Contains(strings.ToLower(item.Plate), needle) })
}
