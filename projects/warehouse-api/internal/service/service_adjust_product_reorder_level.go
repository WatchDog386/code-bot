package service

import "warehouse-api/internal/model"

// AdjustProductReorderLevel adds delta to the reorder level of a product (it can't go below zero).
func (s *Service) AdjustProductReorderLevel(id int, delta int) (model.Product, error) {
	item, err := s.GetProduct(id)
	if err != nil {
		return model.Product{}, err
	}
	value := item.ReorderLevel + delta
	return s.UpdateProduct(id, model.ProductPatch{ReorderLevel: &value})
}

// SetProductCategory moves a product to another category.
func (s *Service) SetProductCategory(id int, value model.ProductCategory) (model.Product, error) {
	return s.UpdateProduct(id, model.ProductPatch{Category: &value})
}

// ToggleProductActive flips the active flag of a product.
func (s *Service) ToggleProductActive(id int) (model.Product, error) {
	item, err := s.GetProduct(id)
	if err != nil {
		return model.Product{}, err
	}
	flipped := !item.Active
	return s.UpdateProduct(id, model.ProductPatch{Active: &flipped})
}

// ProductStats sums up every product.
type ProductStats struct {
	Count               int                           `json:"count"`
	TotalUnitCost       float64                       `json:"total_unit_cost"`
	AverageUnitCost     float64                       `json:"average_unit_cost"`
	TotalUnitPrice      float64                       `json:"total_unit_price"`
	AverageUnitPrice    float64                       `json:"average_unit_price"`
	TotalReorderLevel   int                           `json:"total_reorder_level"`
	AverageReorderLevel float64                       `json:"average_reorder_level"`
	ByCategory          map[model.ProductCategory]int `json:"by_category"`
	Active              int                           `json:"active"`
}
