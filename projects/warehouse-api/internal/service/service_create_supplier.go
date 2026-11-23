package service

import "warehouse-api/internal/model"

// CreateSupplier validates and stores a new supplier.
func (s *Service) CreateSupplier(item model.Supplier) (model.Supplier, error) {
	item.ID = 0
	if err := item.Validate(); err != nil {
		return model.Supplier{}, err
	}
	if err := s.checkSupplierLinks(item); err != nil {
		return model.Supplier{}, err
	}
	return s.Suppliers.Create(item), nil
}

// GetSupplier returns one supplier.
func (s *Service) GetSupplier(id int) (model.Supplier, error) {
	item, ok := s.Suppliers.Get(id)
	if !ok {
		return model.Supplier{}, notFound("supplier", id)
	}
	return item, nil
}

// ListSuppliers returns every supplier, oldest first.
func (s *Service) ListSuppliers() []model.Supplier {
	return s.Suppliers.List()
}
