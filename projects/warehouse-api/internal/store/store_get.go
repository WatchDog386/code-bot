package store

import (
	"sort"

	"warehouse-api/internal/model"
)

// Get returns the record with that id.
func (s *PurchaseOrderStore) Get(id int) (model.PurchaseOrder, bool) {
	s.mu.RLock()
	defer s.mu.RUnlock()
	item, ok := s.items[id]
	return item, ok
}

// List returns every record, oldest first.
func (s *PurchaseOrderStore) List() []model.PurchaseOrder {
	s.mu.RLock()
	defer s.mu.RUnlock()
	out := make([]model.PurchaseOrder, 0, len(s.items))
	for _, item := range s.items {
		out = append(out, item)
	}
	sort.Slice(out, func(i, j int) bool { return out[i].ID < out[j].ID })
	return out
}

// Update replaces an existing record; false if there is none.
func (s *PurchaseOrderStore) Update(item model.PurchaseOrder) bool {
	s.mu.Lock()
	defer s.mu.Unlock()
	if _, ok := s.items[item.ID]; !ok {
		return false
	}
	s.items[item.ID] = item
	return true
}

// Delete removes a record; false if there was none.
func (s *PurchaseOrderStore) Delete(id int) bool {
	s.mu.Lock()
	defer s.mu.Unlock()
	if _, ok := s.items[id]; !ok {
		return false
	}
	delete(s.items, id)
	return true
}

// Count is the number of records.
func (s *PurchaseOrderStore) Count() int {
	s.mu.RLock()
	defer s.mu.RUnlock()
	return len(s.items)
}
