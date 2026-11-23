package store

import (
	"strings"

	"warehouse-api/internal/model"
)

// SearchCountry returns records whose country contains text (any case).
func (s *SupplierStore) SearchCountry(text string) []model.Supplier {
	needle := strings.ToLower(strings.TrimSpace(text))
	return s.Filter(func(item model.Supplier) bool { return strings.Contains(strings.ToLower(item.Country), needle) })
}

// BetweenLeadDays returns records whose lead days is within [low, high].
func (s *SupplierStore) BetweenLeadDays(low, high int) []model.Supplier {
	return s.Filter(func(item model.Supplier) bool { return item.LeadDays >= low && item.LeadDays <= high })
}

// TotalLeadDays adds up the lead days of every record.
func (s *SupplierStore) TotalLeadDays() int {
	var total int
	for _, item := range s.List() {
		total += item.LeadDays
	}
	return total
}

// AverageLeadDays is the mean lead days (0 when there are no records).
func (s *SupplierStore) AverageLeadDays() float64 {
	items := s.List()
	if len(items) == 0 {
		return 0
	}
	return float64(s.TotalLeadDays()) / float64(len(items))
}

// MaxLeadDays returns the record with the highest lead days.
func (s *SupplierStore) MaxLeadDays() (model.Supplier, bool) {
	var best model.Supplier
	found := false
	for _, item := range s.List() {
		if !found || item.LeadDays > best.LeadDays {
			best, found = item, true
		}
	}
	return best, found
}

// WherePreferred returns records whose preferred flag equals flag.
func (s *SupplierStore) WherePreferred(flag bool) []model.Supplier {
	return s.Filter(func(item model.Supplier) bool { return item.Preferred == flag })
}
