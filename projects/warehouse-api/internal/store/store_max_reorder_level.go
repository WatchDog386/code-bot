package store

import (
	"strings"
	"sync"

	"warehouse-api/internal/model"
)

// MaxReorderLevel returns the record with the highest reorder level.
func (s *ProductStore) MaxReorderLevel() (model.Product, bool) {
	var best model.Product
	found := false
	for _, item := range s.List() {
		if !found || item.ReorderLevel > best.ReorderLevel {
			best, found = item, true
		}
	}
	return best, found
}

// WithCategory returns records whose category is value.
func (s *ProductStore) WithCategory(value model.ProductCategory) []model.Product {
	return s.Filter(func(item model.Product) bool { return item.Category == value })
}

// CountByCategory counts records for every category.
func (s *ProductStore) CountByCategory() map[model.ProductCategory]int {
	counts := map[model.ProductCategory]int{}
	for _, v := range model.ProductCategoryValues {
		counts[v] = 0
	}
	for _, item := range s.List() {
		counts[item.Category]++
	}
	return counts
}

// WhereActive returns records whose active flag equals flag.
func (s *ProductStore) WhereActive(flag bool) []model.Product {
	return s.Filter(func(item model.Product) bool { return item.Active == flag })
}

// Search returns records where any text field contains text (any case).
func (s *ProductStore) Search(text string) []model.Product {
	needle := strings.ToLower(strings.TrimSpace(text))
	return s.Filter(func(item model.Product) bool {
		for _, value := range []string{item.Sku, item.Name} {
			if strings.Contains(strings.ToLower(value), needle) {
				return true
			}
		}
		return false
	})
}

// BinStore keeps every bin.
type BinStore struct {
	mu     sync.RWMutex
	items  map[int]model.Bin
	nextID int
}

// NewBinStore returns an empty store.
func NewBinStore() *BinStore {
	return &BinStore{items: map[int]model.Bin{}, nextID: 1}
}

// Create stores item under the next id and returns it.
func (s *BinStore) Create(item model.Bin) model.Bin {
	s.mu.Lock()
	defer s.mu.Unlock()
	item.ID = s.nextID
	s.nextID++
	s.items[item.ID] = item
	return item
}

// Get returns the record with that id.
func (s *BinStore) Get(id int) (model.Bin, bool) {
	s.mu.RLock()
	defer s.mu.RUnlock()
	item, ok := s.items[id]
	return item, ok
}
