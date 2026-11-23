package store

import (
	"strings"

	"warehouse-api/internal/model"
)

// Filter returns the records keep() accepts, oldest first.
func (s *ProductStore) Filter(keep func(model.Product) bool) []model.Product {
	out := []model.Product{}
	for _, item := range s.List() {
		if keep(item) {
			out = append(out, item)
		}
	}
	return out
}

// ForSupplier returns records linked to supplier id.
func (s *ProductStore) ForSupplier(id int) []model.Product {
	return s.Filter(func(item model.Product) bool { return item.SupplierID == id })
}

// CountForSupplier counts records linked to supplier id.
func (s *ProductStore) CountForSupplier(id int) int {
	return len(s.ForSupplier(id))
}

// FindBySku returns records whose sku is exactly value.
func (s *ProductStore) FindBySku(value string) []model.Product {
	return s.Filter(func(item model.Product) bool { return item.Sku == value })
}

// SearchSku returns records whose sku contains text (any case).
func (s *ProductStore) SearchSku(text string) []model.Product {
	needle := strings.ToLower(strings.TrimSpace(text))
	return s.Filter(func(item model.Product) bool { return strings.Contains(strings.ToLower(item.Sku), needle) })
}

// FindByName returns records whose name is exactly value.
func (s *ProductStore) FindByName(value string) []model.Product {
	return s.Filter(func(item model.Product) bool { return item.Name == value })
}

// SearchName returns records whose name contains text (any case).
func (s *ProductStore) SearchName(text string) []model.Product {
	needle := strings.ToLower(strings.TrimSpace(text))
	return s.Filter(func(item model.Product) bool { return strings.Contains(strings.ToLower(item.Name), needle) })
}

// BetweenUnitCost returns records whose unit cost is within [low, high].
func (s *ProductStore) BetweenUnitCost(low, high float64) []model.Product {
	return s.Filter(func(item model.Product) bool { return item.UnitCost >= low && item.UnitCost <= high })
}

// TotalUnitCost adds up the unit cost of every record.
func (s *ProductStore) TotalUnitCost() float64 {
	var total float64
	for _, item := range s.List() {
		total += item.UnitCost
	}
	return total
}

// AverageUnitCost is the mean unit cost (0 when there are no records).
func (s *ProductStore) AverageUnitCost() float64 {
	items := s.List()
	if len(items) == 0 {
		return 0
	}
	return float64(s.TotalUnitCost()) / float64(len(items))
}

// MaxUnitCost returns the record with the highest unit cost.
func (s *ProductStore) MaxUnitCost() (model.Product, bool) {
	var best model.Product
	found := false
	for _, item := range s.List() {
		if !found || item.UnitCost > best.UnitCost {
			best, found = item, true
		}
	}
	return best, found
}

// BetweenUnitPrice returns records whose unit price is within [low, high].
func (s *ProductStore) BetweenUnitPrice(low, high float64) []model.Product {
	return s.Filter(func(item model.Product) bool { return item.UnitPrice >= low && item.UnitPrice <= high })
}
