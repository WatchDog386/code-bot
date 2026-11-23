package store

import "warehouse-api/internal/model"

// TotalTotal adds up the total of every record.
func (s *PurchaseOrderStore) TotalTotal() float64 {
	var total float64
	for _, item := range s.List() {
		total += item.Total
	}
	return total
}

// AverageTotal is the mean total (0 when there are no records).
func (s *PurchaseOrderStore) AverageTotal() float64 {
	items := s.List()
	if len(items) == 0 {
		return 0
	}
	return float64(s.TotalTotal()) / float64(len(items))
}

// MaxTotal returns the record with the highest total.
func (s *PurchaseOrderStore) MaxTotal() (model.PurchaseOrder, bool) {
	var best model.PurchaseOrder
	found := false
	for _, item := range s.List() {
		if !found || item.Total > best.Total {
			best, found = item, true
		}
	}
	return best, found
}

// WithStatus returns records whose status is value.
func (s *PurchaseOrderStore) WithStatus(value model.PurchaseOrderStatus) []model.PurchaseOrder {
	return s.Filter(func(item model.PurchaseOrder) bool { return item.Status == value })
}

// CountByStatus counts records for every status.
func (s *PurchaseOrderStore) CountByStatus() map[model.PurchaseOrderStatus]int {
	counts := map[model.PurchaseOrderStatus]int{}
	for _, v := range model.PurchaseOrderStatusValues {
		counts[v] = 0
	}
	for _, item := range s.List() {
		counts[item.Status]++
	}
	return counts
}
