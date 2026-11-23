// Package store keeps the Warehouse Inventory records in memory, safe for concurrent use.
package store

import (
	"sync"

	"warehouse-api/internal/model"
)

// SupplierStore keeps every supplier.
type SupplierStore struct {
	mu     sync.RWMutex
	items  map[int]model.Supplier
	nextID int
}

// NewSupplierStore returns an empty store.
func NewSupplierStore() *SupplierStore {
	return &SupplierStore{items: map[int]model.Supplier{}, nextID: 1}
}

// Create stores item under the next id and returns it.
func (s *SupplierStore) Create(item model.Supplier) model.Supplier {
	s.mu.Lock()
	defer s.mu.Unlock()
	item.ID = s.nextID
	s.nextID++
	s.items[item.ID] = item
	return item
}

// Get returns the record with that id.
func (s *SupplierStore) Get(id int) (model.Supplier, bool) {
	s.mu.RLock()
	defer s.mu.RUnlock()
	item, ok := s.items[id]
	return item, ok
}
