package store

import (
	"sort"
	"sync"

	"fleet-api/internal/model"
)

// DriverStore keeps every driver.
type DriverStore struct {
	mu     sync.RWMutex
	items  map[int]model.Driver
	nextID int
}

// NewDriverStore returns an empty store.
func NewDriverStore() *DriverStore {
	return &DriverStore{items: map[int]model.Driver{}, nextID: 1}
}

// Create stores item under the next id and returns it.
func (s *DriverStore) Create(item model.Driver) model.Driver {
	s.mu.Lock()
	defer s.mu.Unlock()
	item.ID = s.nextID
	s.nextID++
	s.items[item.ID] = item
	return item
}

// Get returns the record with that id.
func (s *DriverStore) Get(id int) (model.Driver, bool) {
	s.mu.RLock()
	defer s.mu.RUnlock()
	item, ok := s.items[id]
	return item, ok
}

// List returns every record, oldest first.
func (s *DriverStore) List() []model.Driver {
	s.mu.RLock()
	defer s.mu.RUnlock()
	out := make([]model.Driver, 0, len(s.items))
	for _, item := range s.items {
		out = append(out, item)
	}
	sort.Slice(out, func(i, j int) bool { return out[i].ID < out[j].ID })
	return out
}

// Update replaces an existing record; false if there is none.
func (s *DriverStore) Update(item model.Driver) bool {
	s.mu.Lock()
	defer s.mu.Unlock()
	if _, ok := s.items[item.ID]; !ok {
		return false
	}
	s.items[item.ID] = item
	return true
}

// Delete removes a record; false if there was none.
func (s *DriverStore) Delete(id int) bool {
	s.mu.Lock()
	defer s.mu.Unlock()
	if _, ok := s.items[id]; !ok {
		return false
	}
	delete(s.items, id)
	return true
}

// Count is the number of records.
func (s *DriverStore) Count() int {
	s.mu.RLock()
	defer s.mu.RUnlock()
	return len(s.items)
}

// Filter returns the records keep() accepts, oldest first.
func (s *DriverStore) Filter(keep func(model.Driver) bool) []model.Driver {
	out := []model.Driver{}
	for _, item := range s.List() {
		if keep(item) {
			out = append(out, item)
		}
	}
	return out
}

// FindByName returns records whose name is exactly value.
func (s *DriverStore) FindByName(value string) []model.Driver {
	return s.Filter(func(item model.Driver) bool { return item.Name == value })
}
