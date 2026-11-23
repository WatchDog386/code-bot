package store

import (
	"strings"
	"sync"

	"warehouse-api/internal/model"
)

// Search returns records where any text field contains text (any case).
func (s *SupplierStore) Search(text string) []model.Supplier {
	needle := strings.ToLower(strings.TrimSpace(text))
	return s.Filter(func(item model.Supplier) bool {
		for _, value := range []string{item.Name, item.Email, item.Phone, item.Country} {
			if strings.Contains(strings.ToLower(value), needle) {
				return true
			}
		}
		return false
	})
}

// ProductStore keeps every product.
type ProductStore struct {
	mu     sync.RWMutex
	items  map[int]model.Product
	nextID int
}

// NewProductStore returns an empty store.
func NewProductStore() *ProductStore {
	return &ProductStore{items: map[int]model.Product{}, nextID: 1}
}

// Create stores item under the next id and returns it.
func (s *ProductStore) Create(item model.Product) model.Product {
	s.mu.Lock()
	defer s.mu.Unlock()
	item.ID = s.nextID
	s.nextID++
	s.items[item.ID] = item
	return item
}

// Get returns the record with that id.
func (s *ProductStore) Get(id int) (model.Product, bool) {
	s.mu.RLock()
	defer s.mu.RUnlock()
	item, ok := s.items[id]
	return item, ok
}
