package store

import (
	"sort"

	"warehouse-api/internal/model"
)

// Create stores item under the next id and returns it.
func (s *StockMovementStore) Create(item model.StockMovement) model.StockMovement {
	s.mu.Lock()
	defer s.mu.Unlock()
	item.ID = s.nextID
	s.nextID++
	s.items[item.ID] = item
	return item
}

// Get returns the record with that id.
func (s *StockMovementStore) Get(id int) (model.StockMovement, bool) {
	s.mu.RLock()
	defer s.mu.RUnlock()
	item, ok := s.items[id]
	return item, ok
}

// List returns every record, oldest first.
func (s *StockMovementStore) List() []model.StockMovement {
	s.mu.RLock()
	defer s.mu.RUnlock()
	out := make([]model.StockMovement, 0, len(s.items))
	for _, item := range s.items {
		out = append(out, item)
	}
	sort.Slice(out, func(i, j int) bool { return out[i].ID < out[j].ID })
	return out
}

// Update replaces an existing record; false if there is none.
func (s *StockMovementStore) Update(item model.StockMovement) bool {
	s.mu.Lock()
	defer s.mu.Unlock()
	if _, ok := s.items[item.ID]; !ok {
		return false
	}
	s.items[item.ID] = item
	return true
}

// Delete removes a record; false if there was none.
func (s *StockMovementStore) Delete(id int) bool {
	s.mu.Lock()
	defer s.mu.Unlock()
	if _, ok := s.items[id]; !ok {
		return false
	}
	delete(s.items, id)
	return true
}

// Count is the number of records.
func (s *StockMovementStore) Count() int {
	s.mu.RLock()
	defer s.mu.RUnlock()
	return len(s.items)
}

// Filter returns the records keep() accepts, oldest first.
func (s *StockMovementStore) Filter(keep func(model.StockMovement) bool) []model.StockMovement {
	out := []model.StockMovement{}
	for _, item := range s.List() {
		if keep(item) {
			out = append(out, item)
		}
	}
	return out
}

// ForProduct returns records linked to product id.
func (s *StockMovementStore) ForProduct(id int) []model.StockMovement {
	return s.Filter(func(item model.StockMovement) bool { return item.ProductID == id })
}

// CountForProduct counts records linked to product id.
func (s *StockMovementStore) CountForProduct(id int) int {
	return len(s.ForProduct(id))
}

// ForBin returns records linked to bin id.
func (s *StockMovementStore) ForBin(id int) []model.StockMovement {
	return s.Filter(func(item model.StockMovement) bool { return item.BinID == id })
}

// CountForBin counts records linked to bin id.
func (s *StockMovementStore) CountForBin(id int) int {
	return len(s.ForBin(id))
}
