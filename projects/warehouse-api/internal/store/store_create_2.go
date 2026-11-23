package store

import (
	"sort"

	"warehouse-api/internal/model"
)

// Create stores item under the next id and returns it.
func (s *StockCountStore) Create(item model.StockCount) model.StockCount {
	s.mu.Lock()
	defer s.mu.Unlock()
	item.ID = s.nextID
	s.nextID++
	s.items[item.ID] = item
	return item
}

// Get returns the record with that id.
func (s *StockCountStore) Get(id int) (model.StockCount, bool) {
	s.mu.RLock()
	defer s.mu.RUnlock()
	item, ok := s.items[id]
	return item, ok
}

// List returns every record, oldest first.
func (s *StockCountStore) List() []model.StockCount {
	s.mu.RLock()
	defer s.mu.RUnlock()
	out := make([]model.StockCount, 0, len(s.items))
	for _, item := range s.items {
		out = append(out, item)
	}
	sort.Slice(out, func(i, j int) bool { return out[i].ID < out[j].ID })
	return out
}

// Update replaces an existing record; false if there is none.
func (s *StockCountStore) Update(item model.StockCount) bool {
	s.mu.Lock()
	defer s.mu.Unlock()
	if _, ok := s.items[item.ID]; !ok {
		return false
	}
	s.items[item.ID] = item
	return true
}

// Delete removes a record; false if there was none.
func (s *StockCountStore) Delete(id int) bool {
	s.mu.Lock()
	defer s.mu.Unlock()
	if _, ok := s.items[id]; !ok {
		return false
	}
	delete(s.items, id)
	return true
}

// Count is the number of records.
func (s *StockCountStore) Count() int {
	s.mu.RLock()
	defer s.mu.RUnlock()
	return len(s.items)
}

// Filter returns the records keep() accepts, oldest first.
func (s *StockCountStore) Filter(keep func(model.StockCount) bool) []model.StockCount {
	out := []model.StockCount{}
	for _, item := range s.List() {
		if keep(item) {
			out = append(out, item)
		}
	}
	return out
}
