// Package store keeps the Fleet Management records in memory, safe for concurrent use.
package store

import (
	"sort"
	"sync"

	"fleet-api/internal/model"
)

// VehicleStore keeps every vehicle.
type VehicleStore struct {
	mu     sync.RWMutex
	items  map[int]model.Vehicle
	nextID int
}

// NewVehicleStore returns an empty store.
func NewVehicleStore() *VehicleStore {
	return &VehicleStore{items: map[int]model.Vehicle{}, nextID: 1}
}

// Create stores item under the next id and returns it.
func (s *VehicleStore) Create(item model.Vehicle) model.Vehicle {
	s.mu.Lock()
	defer s.mu.Unlock()
	item.ID = s.nextID
	s.nextID++
	s.items[item.ID] = item
	return item
}

// Get returns the record with that id.
func (s *VehicleStore) Get(id int) (model.Vehicle, bool) {
	s.mu.RLock()
	defer s.mu.RUnlock()
	item, ok := s.items[id]
	return item, ok
}

// List returns every record, oldest first.
func (s *VehicleStore) List() []model.Vehicle {
	s.mu.RLock()
	defer s.mu.RUnlock()
	out := make([]model.Vehicle, 0, len(s.items))
	for _, item := range s.items {
		out = append(out, item)
	}
	sort.Slice(out, func(i, j int) bool { return out[i].ID < out[j].ID })
	return out
}
