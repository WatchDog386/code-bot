package store

import (
	"strings"

	"library-api/internal/model"
)

// Update replaces an existing record; false if there is none.
func (s *AuthorStore) Update(item model.Author) bool {
	s.mu.Lock()
	defer s.mu.Unlock()
	if _, ok := s.items[item.ID]; !ok {
		return false
	}
	s.items[item.ID] = item
	return true
}

// Delete removes a record; false if there was none.
func (s *AuthorStore) Delete(id int) bool {
	s.mu.Lock()
	defer s.mu.Unlock()
	if _, ok := s.items[id]; !ok {
		return false
	}
	delete(s.items, id)
	return true
}

// Count is the number of records.
func (s *AuthorStore) Count() int {
	s.mu.RLock()
	defer s.mu.RUnlock()
	return len(s.items)
}

// Filter returns the records keep() accepts, oldest first.
func (s *AuthorStore) Filter(keep func(model.Author) bool) []model.Author {
	out := []model.Author{}
	for _, item := range s.List() {
		if keep(item) {
			out = append(out, item)
		}
	}
	return out
}

// FindByName returns records whose name is exactly value.
func (s *AuthorStore) FindByName(value string) []model.Author {
	return s.Filter(func(item model.Author) bool { return item.Name == value })
}

// SearchName returns records whose name contains text (any case).
func (s *AuthorStore) SearchName(text string) []model.Author {
	needle := strings.ToLower(strings.TrimSpace(text))
	return s.Filter(func(item model.Author) bool { return strings.Contains(strings.ToLower(item.Name), needle) })
}
