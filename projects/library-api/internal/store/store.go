// Package store keeps the Library Circulation records in memory, safe for concurrent use.
package store

import (
	"sort"
	"sync"

	"library-api/internal/model"
)

// AuthorStore keeps every author.
type AuthorStore struct {
	mu     sync.RWMutex
	items  map[int]model.Author
	nextID int
}

// NewAuthorStore returns an empty store.
func NewAuthorStore() *AuthorStore {
	return &AuthorStore{items: map[int]model.Author{}, nextID: 1}
}

// Create stores item under the next id and returns it.
func (s *AuthorStore) Create(item model.Author) model.Author {
	s.mu.Lock()
	defer s.mu.Unlock()
	item.ID = s.nextID
	s.nextID++
	s.items[item.ID] = item
	return item
}

// Get returns the record with that id.
func (s *AuthorStore) Get(id int) (model.Author, bool) {
	s.mu.RLock()
	defer s.mu.RUnlock()
	item, ok := s.items[id]
	return item, ok
}

// List returns every record, oldest first.
func (s *AuthorStore) List() []model.Author {
	s.mu.RLock()
	defer s.mu.RUnlock()
	out := make([]model.Author, 0, len(s.items))
	for _, item := range s.items {
		out = append(out, item)
	}
	sort.Slice(out, func(i, j int) bool { return out[i].ID < out[j].ID })
	return out
}
