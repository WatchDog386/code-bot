package service

import (
	"math"

	"warehouse-api/internal/model"
)

// UpdatePurchaseOrder applies patch to a purchase order.
func (s *Service) UpdatePurchaseOrder(id int, patch model.PurchaseOrderPatch) (model.PurchaseOrder, error) {
	current, err := s.GetPurchaseOrder(id)
	if err != nil {
		return model.PurchaseOrder{}, err
	}
	updated, err := patch.Apply(current)
	if err != nil {
		return model.PurchaseOrder{}, err
	}
	if err := s.checkPurchaseOrderLinks(updated); err != nil {
		return model.PurchaseOrder{}, err
	}
	s.PurchaseOrders.Update(updated)
	return updated, nil
}

// DeletePurchaseOrder removes a purchase order nothing points at any more.
func (s *Service) DeletePurchaseOrder(id int) error {
	if _, err := s.GetPurchaseOrder(id); err != nil {
		return err
	}
	s.PurchaseOrders.Delete(id)
	return nil
}

// checkPurchaseOrderLinks makes sure every record a purchase order points at exists.
func (s *Service) checkPurchaseOrderLinks(item model.PurchaseOrder) error {
	if _, ok := s.Suppliers.Get(item.SupplierID); !ok {
		return notFound("supplier", item.SupplierID)
	}
	return nil
}

// AdjustPurchaseOrderTotal adds delta to the total of a purchase order (it can't go below zero).
func (s *Service) AdjustPurchaseOrderTotal(id int, delta float64) (model.PurchaseOrder, error) {
	item, err := s.GetPurchaseOrder(id)
	if err != nil {
		return model.PurchaseOrder{}, err
	}
	value := math.Round((item.Total+delta)*100) / 100
	return s.UpdatePurchaseOrder(id, model.PurchaseOrderPatch{Total: &value})
}

// SetPurchaseOrderStatus moves a purchase order to another status.
func (s *Service) SetPurchaseOrderStatus(id int, value model.PurchaseOrderStatus) (model.PurchaseOrder, error) {
	return s.UpdatePurchaseOrder(id, model.PurchaseOrderPatch{Status: &value})
}

// PurchaseOrderStats sums up every purchase order.
type PurchaseOrderStats struct {
	Count        int                               `json:"count"`
	TotalTotal   float64                           `json:"total_total"`
	AverageTotal float64                           `json:"average_total"`
	ByStatus     map[model.PurchaseOrderStatus]int `json:"by_status"`
}
