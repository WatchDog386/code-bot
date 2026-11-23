package store

import (
	"strings"

	"warehouse-api/internal/model"
)

// Filter returns the records keep() accepts, oldest first.
func (s *SupplierStore) Filter(keep func(model.Supplier) bool) []model.Supplier {
	out := []model.Supplier{}
	for _, item := range s.List() {
		if keep(item) {
			out = append(out, item)
		}
	}
	return out
}

// FindByName returns records whose name is exactly value.
func (s *SupplierStore) FindByName(value string) []model.Supplier {
	return s.Filter(func(item model.Supplier) bool { return item.Name == value })
}

// SearchName returns records whose name contains text (any case).
func (s *SupplierStore) SearchName(text string) []model.Supplier {
	needle := strings.ToLower(strings.TrimSpace(text))
	return s.Filter(func(item model.Supplier) bool { return strings.Contains(strings.ToLower(item.Name), needle) })
}

// FindByEmail returns records whose email is exactly value.
func (s *SupplierStore) FindByEmail(value string) []model.Supplier {
	return s.Filter(func(item model.Supplier) bool { return item.Email == value })
}

// SearchEmail returns records whose email contains text (any case).
func (s *SupplierStore) SearchEmail(text string) []model.Supplier {
	needle := strings.ToLower(strings.TrimSpace(text))
	return s.Filter(func(item model.Supplier) bool { return strings.Contains(strings.ToLower(item.Email), needle) })
}

// FindByPhone returns records whose phone is exactly value.
func (s *SupplierStore) FindByPhone(value string) []model.Supplier {
	return s.Filter(func(item model.Supplier) bool { return item.Phone == value })
}

// SearchPhone returns records whose phone contains text (any case).
func (s *SupplierStore) SearchPhone(text string) []model.Supplier {
	needle := strings.ToLower(strings.TrimSpace(text))
	return s.Filter(func(item model.Supplier) bool { return strings.Contains(strings.ToLower(item.Phone), needle) })
}

// FindByCountry returns records whose country is exactly value.
func (s *SupplierStore) FindByCountry(value string) []model.Supplier {
	return s.Filter(func(item model.Supplier) bool { return item.Country == value })
}
