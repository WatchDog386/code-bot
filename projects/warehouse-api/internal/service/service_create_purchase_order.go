package service

import "warehouse-api/internal/model"

// CreatePurchaseOrder validates and stores a new purchase order.
func (s *Service) CreatePurchaseOrder(item model.PurchaseOrder) (model.PurchaseOrder, error) {
	item.ID = 0
	if err := item.Validate(); err != nil {
		return model.PurchaseOrder{}, err
	}
	if err := s.checkPurchaseOrderLinks(item); err != nil {
		return model.PurchaseOrder{}, err
	}
	return s.PurchaseOrders.Create(item), nil
}

// GetPurchaseOrder returns one purchase order.
func (s *Service) GetPurchaseOrder(id int) (model.PurchaseOrder, error) {
	item, ok := s.PurchaseOrders.Get(id)
	if !ok {
		return model.PurchaseOrder{}, notFound("purchase order", id)
	}
	return item, nil
}

// ListPurchaseOrders returns every purchase order, oldest first.
func (s *Service) ListPurchaseOrders() []model.PurchaseOrder {
	return s.PurchaseOrders.List()
}
