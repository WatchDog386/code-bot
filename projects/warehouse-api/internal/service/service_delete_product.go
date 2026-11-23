package service

import (
	"math"

	"warehouse-api/internal/model"
)

// DeleteProduct removes a product nothing points at any more.
func (s *Service) DeleteProduct(id int) error {
	if _, err := s.GetProduct(id); err != nil {
		return err
	}
	if n := s.StockMovements.CountForProduct(id); n > 0 {
		return inUse("product", id, n, "stock movements")
	}
	if n := s.StockCounts.CountForProduct(id); n > 0 {
		return inUse("product", id, n, "stock counts")
	}
	s.Products.Delete(id)
	return nil
}

// checkProductLinks makes sure every record a product points at exists.
func (s *Service) checkProductLinks(item model.Product) error {
	if _, ok := s.Suppliers.Get(item.SupplierID); !ok {
		return notFound("supplier", item.SupplierID)
	}
	return nil
}

// AdjustProductUnitCost adds delta to the unit cost of a product (it can't go below zero).
func (s *Service) AdjustProductUnitCost(id int, delta float64) (model.Product, error) {
	item, err := s.GetProduct(id)
	if err != nil {
		return model.Product{}, err
	}
	value := math.Round((item.UnitCost+delta)*100) / 100
	return s.UpdateProduct(id, model.ProductPatch{UnitCost: &value})
}

// AdjustProductUnitPrice adds delta to the unit price of a product (it can't go below zero).
func (s *Service) AdjustProductUnitPrice(id int, delta float64) (model.Product, error) {
	item, err := s.GetProduct(id)
	if err != nil {
		return model.Product{}, err
	}
	value := math.Round((item.UnitPrice+delta)*100) / 100
	return s.UpdateProduct(id, model.ProductPatch{UnitPrice: &value})
}
