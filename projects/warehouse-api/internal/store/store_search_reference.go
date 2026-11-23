package store

import (
	"strings"
	"sync"

	"warehouse-api/internal/model"
)

// SearchReference returns records whose reference contains text (any case).
func (s *StockMovementStore) SearchReference(text string) []model.StockMovement {
	needle := strings.ToLower(strings.TrimSpace(text))
	return s.Filter(func(item model.StockMovement) bool { return strings.Contains(strings.ToLower(item.Reference), needle) })
}

// Search returns records where any text field contains text (any case).
func (s *StockMovementStore) Search(text string) []model.StockMovement {
	needle := strings.ToLower(strings.TrimSpace(text))
	return s.Filter(func(item model.StockMovement) bool {
		for _, value := range []string{item.Reference} {
			if strings.Contains(strings.ToLower(value), needle) {
				return true
			}
		}
		return false
	})
}

// PurchaseOrderStore keeps every purchase order.
type PurchaseOrderStore struct {
	mu     sync.RWMutex
	items  map[int]model.PurchaseOrder
	nextID int
}

// NewPurchaseOrderStore returns an empty store.
func NewPurchaseOrderStore() *PurchaseOrderStore {
	return &PurchaseOrderStore{items: map[int]model.PurchaseOrder{}, nextID: 1}
}

// Create stores item under the next id and returns it.
func (s *PurchaseOrderStore) Create(item model.PurchaseOrder) model.PurchaseOrder {
	s.mu.Lock()
	defer s.mu.Unlock()
	item.ID = s.nextID
	s.nextID++
	s.items[item.ID] = item
	return item
}
