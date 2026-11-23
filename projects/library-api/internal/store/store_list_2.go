package store

import (
	"sort"

	"library-api/internal/model"
)

// List returns every record, oldest first.
func (s *ReservationStore) List() []model.Reservation {
	s.mu.RLock()
	defer s.mu.RUnlock()
	out := make([]model.Reservation, 0, len(s.items))
	for _, item := range s.items {
		out = append(out, item)
	}
	sort.Slice(out, func(i, j int) bool { return out[i].ID < out[j].ID })
	return out
}

// Update replaces an existing record; false if there is none.
func (s *ReservationStore) Update(item model.Reservation) bool {
	s.mu.Lock()
	defer s.mu.Unlock()
	if _, ok := s.items[item.ID]; !ok {
		return false
	}
	s.items[item.ID] = item
	return true
}

// Delete removes a record; false if there was none.
func (s *ReservationStore) Delete(id int) bool {
	s.mu.Lock()
	defer s.mu.Unlock()
	if _, ok := s.items[id]; !ok {
		return false
	}
	delete(s.items, id)
	return true
}

// Count is the number of records.
func (s *ReservationStore) Count() int {
	s.mu.RLock()
	defer s.mu.RUnlock()
	return len(s.items)
}

// Filter returns the records keep() accepts, oldest first.
func (s *ReservationStore) Filter(keep func(model.Reservation) bool) []model.Reservation {
	out := []model.Reservation{}
	for _, item := range s.List() {
		if keep(item) {
			out = append(out, item)
		}
	}
	return out
}

// ForBook returns records linked to book id.
func (s *ReservationStore) ForBook(id int) []model.Reservation {
	return s.Filter(func(item model.Reservation) bool { return item.BookID == id })
}
