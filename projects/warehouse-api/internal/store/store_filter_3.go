package store

import "warehouse-api/internal/model"

// Filter returns the records keep() accepts, oldest first.
func (s *PurchaseOrderStore) Filter(keep func(model.PurchaseOrder) bool) []model.PurchaseOrder {
	out := []model.PurchaseOrder{}
	for _, item := range s.List() {
		if keep(item) {
			out = append(out, item)
		}
	}
	return out
}

// ForSupplier returns records linked to supplier id.
func (s *PurchaseOrderStore) ForSupplier(id int) []model.PurchaseOrder {
	return s.Filter(func(item model.PurchaseOrder) bool { return item.SupplierID == id })
}

// CountForSupplier counts records linked to supplier id.
func (s *PurchaseOrderStore) CountForSupplier(id int) int {
	return len(s.ForSupplier(id))
}

// OrderedBefore returns records whose ordered is before day (YYYY-MM-DD).
func (s *PurchaseOrderStore) OrderedBefore(day string) []model.PurchaseOrder {
	return s.Filter(func(item model.PurchaseOrder) bool { return item.Ordered < day })
}

// OrderedAfter returns records whose ordered is after day (YYYY-MM-DD).
func (s *PurchaseOrderStore) OrderedAfter(day string) []model.PurchaseOrder {
	return s.Filter(func(item model.PurchaseOrder) bool { return item.Ordered > day })
}

// OrderedOn returns records whose ordered is day.
func (s *PurchaseOrderStore) OrderedOn(day string) []model.PurchaseOrder {
	return s.Filter(func(item model.PurchaseOrder) bool { return item.Ordered == day })
}

// ExpectedBefore returns records whose expected is before day (YYYY-MM-DD).
func (s *PurchaseOrderStore) ExpectedBefore(day string) []model.PurchaseOrder {
	return s.Filter(func(item model.PurchaseOrder) bool { return item.Expected < day })
}

// ExpectedAfter returns records whose expected is after day (YYYY-MM-DD).
func (s *PurchaseOrderStore) ExpectedAfter(day string) []model.PurchaseOrder {
	return s.Filter(func(item model.PurchaseOrder) bool { return item.Expected > day })
}

// ExpectedOn returns records whose expected is day.
func (s *PurchaseOrderStore) ExpectedOn(day string) []model.PurchaseOrder {
	return s.Filter(func(item model.PurchaseOrder) bool { return item.Expected == day })
}

// BetweenTotal returns records whose total is within [low, high].
func (s *PurchaseOrderStore) BetweenTotal(low, high float64) []model.PurchaseOrder {
	return s.Filter(func(item model.PurchaseOrder) bool { return item.Total >= low && item.Total <= high })
}
