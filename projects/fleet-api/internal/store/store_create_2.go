package store

import (
	"sort"

	"fleet-api/internal/model"
)

// Create stores item under the next id and returns it.
func (s *ServiceRecordStore) Create(item model.ServiceRecord) model.ServiceRecord {
	s.mu.Lock()
	defer s.mu.Unlock()
	item.ID = s.nextID
	s.nextID++
	s.items[item.ID] = item
	return item
}

// Get returns the record with that id.
func (s *ServiceRecordStore) Get(id int) (model.ServiceRecord, bool) {
	s.mu.RLock()
	defer s.mu.RUnlock()
	item, ok := s.items[id]
	return item, ok
}

// List returns every record, oldest first.
func (s *ServiceRecordStore) List() []model.ServiceRecord {
	s.mu.RLock()
	defer s.mu.RUnlock()
	out := make([]model.ServiceRecord, 0, len(s.items))
	for _, item := range s.items {
		out = append(out, item)
	}
	sort.Slice(out, func(i, j int) bool { return out[i].ID < out[j].ID })
	return out
}

// Update replaces an existing record; false if there is none.
func (s *ServiceRecordStore) Update(item model.ServiceRecord) bool {
	s.mu.Lock()
	defer s.mu.Unlock()
	if _, ok := s.items[item.ID]; !ok {
		return false
	}
	s.items[item.ID] = item
	return true
}

// Delete removes a record; false if there was none.
func (s *ServiceRecordStore) Delete(id int) bool {
	s.mu.Lock()
	defer s.mu.Unlock()
	if _, ok := s.items[id]; !ok {
		return false
	}
	delete(s.items, id)
	return true
}
