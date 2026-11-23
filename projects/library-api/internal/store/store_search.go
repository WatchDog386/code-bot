package store

import (
	"strings"
	"sync"

	"library-api/internal/model"
)

// Search returns records where any text field contains text (any case).
func (s *AuthorStore) Search(text string) []model.Author {
	needle := strings.ToLower(strings.TrimSpace(text))
	return s.Filter(func(item model.Author) bool {
		for _, value := range []string{item.Name, item.Email, item.Country} {
			if strings.Contains(strings.ToLower(value), needle) {
				return true
			}
		}
		return false
	})
}

// BookStore keeps every book.
type BookStore struct {
	mu     sync.RWMutex
	items  map[int]model.Book
	nextID int
}

// NewBookStore returns an empty store.
func NewBookStore() *BookStore {
	return &BookStore{items: map[int]model.Book{}, nextID: 1}
}

// Create stores item under the next id and returns it.
func (s *BookStore) Create(item model.Book) model.Book {
	s.mu.Lock()
	defer s.mu.Unlock()
	item.ID = s.nextID
	s.nextID++
	s.items[item.ID] = item
	return item
}

// Get returns the record with that id.
func (s *BookStore) Get(id int) (model.Book, bool) {
	s.mu.RLock()
	defer s.mu.RUnlock()
	item, ok := s.items[id]
	return item, ok
}
