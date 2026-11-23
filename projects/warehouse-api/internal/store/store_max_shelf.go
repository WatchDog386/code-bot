package store

import (
	"strings"
	"sync"

	"warehouse-api/internal/model"
)

// MaxShelf returns the record with the highest shelf.
func (s *BinStore) MaxShelf() (model.Bin, bool) {
	var best model.Bin
	found := false
	for _, item := range s.List() {
		if !found || item.Shelf > best.Shelf {
			best, found = item, true
		}
	}
	return best, found
}

// BetweenCapacity returns records whose capacity is within [low, high].
func (s *BinStore) BetweenCapacity(low, high int) []model.Bin {
	return s.Filter(func(item model.Bin) bool { return item.Capacity >= low && item.Capacity <= high })
}

// TotalCapacity adds up the capacity of every record.
func (s *BinStore) TotalCapacity() int {
	var total int
	for _, item := range s.List() {
		total += item.Capacity
	}
	return total
}

// AverageCapacity is the mean capacity (0 when there are no records).
func (s *BinStore) AverageCapacity() float64 {
	items := s.List()
	if len(items) == 0 {
		return 0
	}
	return float64(s.TotalCapacity()) / float64(len(items))
}

// MaxCapacity returns the record with the highest capacity.
func (s *BinStore) MaxCapacity() (model.Bin, bool) {
	var best model.Bin
	found := false
	for _, item := range s.List() {
		if !found || item.Capacity > best.Capacity {
			best, found = item, true
		}
	}
	return best, found
}

// WhereRefrigerated returns records whose refrigerated flag equals flag.
func (s *BinStore) WhereRefrigerated(flag bool) []model.Bin {
	return s.Filter(func(item model.Bin) bool { return item.Refrigerated == flag })
}

// Search returns records where any text field contains text (any case).
func (s *BinStore) Search(text string) []model.Bin {
	needle := strings.ToLower(strings.TrimSpace(text))
	return s.Filter(func(item model.Bin) bool {
		for _, value := range []string{item.Code, item.Aisle} {
			if strings.Contains(strings.ToLower(value), needle) {
				return true
			}
		}
		return false
	})
}

// StockMovementStore keeps every stock movement.
type StockMovementStore struct {
	mu     sync.RWMutex
	items  map[int]model.StockMovement
	nextID int
}

// NewStockMovementStore returns an empty store.
func NewStockMovementStore() *StockMovementStore {
	return &StockMovementStore{items: map[int]model.StockMovement{}, nextID: 1}
}
