package service

import (
	"fmt"

	"warehouse-api/internal/model"
)

// ToggleSupplierPreferred flips the preferred flag of a supplier.
func (s *Service) ToggleSupplierPreferred(id int) (model.Supplier, error) {
	item, err := s.GetSupplier(id)
	if err != nil {
		return model.Supplier{}, err
	}
	flipped := !item.Preferred
	return s.UpdateSupplier(id, model.SupplierPatch{Preferred: &flipped})
}

// SupplierStats sums up every supplier.
type SupplierStats struct {
	Count           int     `json:"count"`
	TotalLeadDays   int     `json:"total_lead_days"`
	AverageLeadDays float64 `json:"average_lead_days"`
	Preferred       int     `json:"preferred"`
}

// SupplierStats returns totals and breakdowns over every supplier.
func (s *Service) SupplierStats() SupplierStats {
	return SupplierStats{
		Count:           s.Suppliers.Count(),
		TotalLeadDays:   s.Suppliers.TotalLeadDays(),
		AverageLeadDays: s.Suppliers.AverageLeadDays(),
		Preferred:       len(s.Suppliers.WherePreferred(true)),
	}
}

// SampleSupplier returns valid data for a new supplier (links point at seeded records).
func SampleSupplier(i int) model.Supplier {
	return model.Supplier{
		Name:      fmt.Sprintf("Supplier name %d", i),
		Email:     fmt.Sprintf("supplier%d@example.com", i),
		Phone:     fmt.Sprintf("Supplier phone %d", i),
		Country:   fmt.Sprintf("Supplier country %d", i),
		LeadDays:  i + 1,
		Preferred: i%2 == 1,
	}
}

// CreateProduct validates and stores a new product.
func (s *Service) CreateProduct(item model.Product) (model.Product, error) {
	item.ID = 0
	if err := item.Validate(); err != nil {
		return model.Product{}, err
	}
	if err := s.checkProductLinks(item); err != nil {
		return model.Product{}, err
	}
	return s.Products.Create(item), nil
}

// GetProduct returns one product.
func (s *Service) GetProduct(id int) (model.Product, error) {
	item, ok := s.Products.Get(id)
	if !ok {
		return model.Product{}, notFound("product", id)
	}
	return item, nil
}

// ListProducts returns every product, oldest first.
func (s *Service) ListProducts() []model.Product {
	return s.Products.List()
}

// UpdateProduct applies patch to a product.
func (s *Service) UpdateProduct(id int, patch model.ProductPatch) (model.Product, error) {
	current, err := s.GetProduct(id)
	if err != nil {
		return model.Product{}, err
	}
	updated, err := patch.Apply(current)
	if err != nil {
		return model.Product{}, err
	}
	if err := s.checkProductLinks(updated); err != nil {
		return model.Product{}, err
	}
	s.Products.Update(updated)
	return updated, nil
}
