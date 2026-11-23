package store

import (
	"strings"
	"sync"

	"warehouse-api/internal/model"
)

// FindByNotes returns records whose notes is exactly value.
func (s *PurchaseOrderStore) FindByNotes(value string) []model.PurchaseOrder {
	return s.Filter(func(item model.PurchaseOrder) bool { return item.Notes == value })
}

// SearchNotes returns records whose notes contains text (any case).
func (s *PurchaseOrderStore) SearchNotes(text string) []model.PurchaseOrder {
	needle := strings.ToLower(strings.TrimSpace(text))
	return s.Filter(func(item model.PurchaseOrder) bool { return strings.Contains(strings.ToLower(item.Notes), needle) })
}

// Search returns records where any text field contains text (any case).
func (s *PurchaseOrderStore) Search(text string) []model.PurchaseOrder {
	needle := strings.ToLower(strings.TrimSpace(text))
	return s.Filter(func(item model.PurchaseOrder) bool {
		for _, value := range []string{item.Notes} {
			if strings.Contains(strings.ToLower(value), needle) {
				return true
			}
		}
		return false
	})
}

// StockCountStore keeps every stock count.
type StockCountStore struct {
	mu     sync.RWMutex
	items  map[int]model.StockCount
	nextID int
}

// NewStockCountStore returns an empty store.
func NewStockCountStore() *StockCountStore {
	return &StockCountStore{items: map[int]model.StockCount{}, nextID: 1}
}
