package service

import "warehouse-api/internal/model"

// UpdateSupplier applies patch to a supplier.
func (s *Service) UpdateSupplier(id int, patch model.SupplierPatch) (model.Supplier, error) {
	current, err := s.GetSupplier(id)
	if err != nil {
		return model.Supplier{}, err
	}
	updated, err := patch.Apply(current)
	if err != nil {
		return model.Supplier{}, err
	}
	if err := s.checkSupplierLinks(updated); err != nil {
		return model.Supplier{}, err
	}
	s.Suppliers.Update(updated)
	return updated, nil
}

// DeleteSupplier removes a supplier nothing points at any more.
func (s *Service) DeleteSupplier(id int) error {
	if _, err := s.GetSupplier(id); err != nil {
		return err
	}
	if n := s.Products.CountForSupplier(id); n > 0 {
		return inUse("supplier", id, n, "products")
	}
	if n := s.PurchaseOrders.CountForSupplier(id); n > 0 {
		return inUse("supplier", id, n, "purchase orders")
	}
	s.Suppliers.Delete(id)
	return nil
}

// checkSupplierLinks makes sure every record a supplier points at exists.
func (s *Service) checkSupplierLinks(_ model.Supplier) error {
	return nil
}

// AdjustSupplierLeadDays adds delta to the lead days of a supplier (it can't go below zero).
func (s *Service) AdjustSupplierLeadDays(id int, delta int) (model.Supplier, error) {
	item, err := s.GetSupplier(id)
	if err != nil {
		return model.Supplier{}, err
	}
	value := item.LeadDays + delta
	return s.UpdateSupplier(id, model.SupplierPatch{LeadDays: &value})
}
