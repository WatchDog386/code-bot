package service

import (
	"fmt"
	"math"

	"warehouse-api/internal/model"
)

// ProductStats returns totals and breakdowns over every product.
func (s *Service) ProductStats() ProductStats {
	return ProductStats{
		Count:               s.Products.Count(),
		TotalUnitCost:       s.Products.TotalUnitCost(),
		AverageUnitCost:     s.Products.AverageUnitCost(),
		TotalUnitPrice:      s.Products.TotalUnitPrice(),
		AverageUnitPrice:    s.Products.AverageUnitPrice(),
		TotalReorderLevel:   s.Products.TotalReorderLevel(),
		AverageReorderLevel: s.Products.AverageReorderLevel(),
		ByCategory:          s.Products.CountByCategory(),
		Active:              len(s.Products.WhereActive(true)),
	}
}

// SampleProduct returns valid data for a new product (links point at seeded records).
func SampleProduct(i int) model.Product {
	return model.Product{
		SupplierID:   (i-1)%3 + 1,
		Sku:          fmt.Sprintf("Product sku %d", i),
		Name:         fmt.Sprintf("Product name %d", i),
		UnitCost:     math.Round((10*float64(i)+0.99)*100) / 100,
		UnitPrice:    math.Round((10*float64(i)+0.99)*100) / 100,
		ReorderLevel: i + 1,
		Category:     model.ProductCategoryValues[i%5],
		Active:       i%2 == 1,
	}
}
