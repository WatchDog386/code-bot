package store

import (
	"sort"

	"library-api/internal/model"
)

// Create stores item under the next id and returns it.
func (s *LoanStore) Create(item model.Loan) model.Loan {
	s.mu.Lock()
	defer s.mu.Unlock()
	item.ID = s.nextID
	s.nextID++
	s.items[item.ID] = item
	return item
}

// Get returns the record with that id.
func (s *LoanStore) Get(id int) (model.Loan, bool) {
	s.mu.RLock()
	defer s.mu.RUnlock()
	item, ok := s.items[id]
	return item, ok
}

// List returns every record, oldest first.
func (s *LoanStore) List() []model.Loan {
	s.mu.RLock()
	defer s.mu.RUnlock()
	out := make([]model.Loan, 0, len(s.items))
	for _, item := range s.items {
		out = append(out, item)
	}
	sort.Slice(out, func(i, j int) bool { return out[i].ID < out[j].ID })
	return out
}

// Update replaces an existing record; false if there is none.
func (s *LoanStore) Update(item model.Loan) bool {
	s.mu.Lock()
	defer s.mu.Unlock()
	if _, ok := s.items[item.ID]; !ok {
		return false
	}
	s.items[item.ID] = item
	return true
}

// Delete removes a record; false if there was none.
func (s *LoanStore) Delete(id int) bool {
	s.mu.Lock()
	defer s.mu.Unlock()
	if _, ok := s.items[id]; !ok {
		return false
	}
	delete(s.items, id)
	return true
}

// Count is the number of records.
func (s *LoanStore) Count() int {
	s.mu.RLock()
	defer s.mu.RUnlock()
	return len(s.items)
}

// Filter returns the records keep() accepts, oldest first.
func (s *LoanStore) Filter(keep func(model.Loan) bool) []model.Loan {
	out := []model.Loan{}
	for _, item := range s.List() {
		if keep(item) {
			out = append(out, item)
		}
	}
	return out
}

// ForBook returns records linked to book id.
func (s *LoanStore) ForBook(id int) []model.Loan {
	return s.Filter(func(item model.Loan) bool { return item.BookID == id })
}

// CountForBook counts records linked to book id.
func (s *LoanStore) CountForBook(id int) int {
	return len(s.ForBook(id))
}

// ForMember returns records linked to member id.
func (s *LoanStore) ForMember(id int) []model.Loan {
	return s.Filter(func(item model.Loan) bool { return item.MemberID == id })
}

// CountForMember counts records linked to member id.
func (s *LoanStore) CountForMember(id int) int {
	return len(s.ForMember(id))
}
