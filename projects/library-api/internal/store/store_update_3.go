package store

import (
	"strings"

	"library-api/internal/model"
)

// Update replaces an existing record; false if there is none.
func (s *BranchStore) Update(item model.Branch) bool {
	s.mu.Lock()
	defer s.mu.Unlock()
	if _, ok := s.items[item.ID]; !ok {
		return false
	}
	s.items[item.ID] = item
	return true
}

// Delete removes a record; false if there was none.
func (s *BranchStore) Delete(id int) bool {
	s.mu.Lock()
	defer s.mu.Unlock()
	if _, ok := s.items[id]; !ok {
		return false
	}
	delete(s.items, id)
	return true
}

// Count is the number of records.
func (s *BranchStore) Count() int {
	s.mu.RLock()
	defer s.mu.RUnlock()
	return len(s.items)
}

// Filter returns the records keep() accepts, oldest first.
func (s *BranchStore) Filter(keep func(model.Branch) bool) []model.Branch {
	out := []model.Branch{}
	for _, item := range s.List() {
		if keep(item) {
			out = append(out, item)
		}
	}
	return out
}

// FindByName returns records whose name is exactly value.
func (s *BranchStore) FindByName(value string) []model.Branch {
	return s.Filter(func(item model.Branch) bool { return item.Name == value })
}

// SearchName returns records whose name contains text (any case).
func (s *BranchStore) SearchName(text string) []model.Branch {
	needle := strings.ToLower(strings.TrimSpace(text))
	return s.Filter(func(item model.Branch) bool { return strings.Contains(strings.ToLower(item.Name), needle) })
}

// FindByCity returns records whose city is exactly value.
func (s *BranchStore) FindByCity(value string) []model.Branch {
	return s.Filter(func(item model.Branch) bool { return item.City == value })
}

// SearchCity returns records whose city contains text (any case).
func (s *BranchStore) SearchCity(text string) []model.Branch {
	needle := strings.ToLower(strings.TrimSpace(text))
	return s.Filter(func(item model.Branch) bool { return strings.Contains(strings.ToLower(item.City), needle) })
}
