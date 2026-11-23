package service

import (
	"fmt"
	"math"

	"warehouse-api/internal/model"
)

// PurchaseOrderStats returns totals and breakdowns over every purchase order.
func (s *Service) PurchaseOrderStats() PurchaseOrderStats {
	return PurchaseOrderStats{
		Count:        s.PurchaseOrders.Count(),
		TotalTotal:   s.PurchaseOrders.TotalTotal(),
		AverageTotal: s.PurchaseOrders.AverageTotal(),
		ByStatus:     s.PurchaseOrders.CountByStatus(),
	}
}

// SamplePurchaseOrder returns valid data for a new purchase order (links point at seeded records).
func SamplePurchaseOrder(i int) model.PurchaseOrder {
	return model.PurchaseOrder{
		SupplierID: (i-1)%3 + 1,
		Ordered:    fmt.Sprintf("2026-%02d-%02d", i%12+1, i%28+1),
		Expected:   fmt.Sprintf("2026-%02d-%02d", i%12+1, i%28+1),
		Total:      math.Round((10*float64(i)+0.99)*100) / 100,
		Status:     model.PurchaseOrderStatusValues[i%5],
		Notes:      fmt.Sprintf("Notes about purchase order %d.", i),
	}
}

// CreateStockCount validates and stores a new stock count.
func (s *Service) CreateStockCount(item model.StockCount) (model.StockCount, error) {
	item.ID = 0
	if err := item.Validate(); err != nil {
		return model.StockCount{}, err
	}
	if err := s.checkStockCountLinks(item); err != nil {
		return model.StockCount{}, err
	}
	return s.StockCounts.Create(item), nil
}

// GetStockCount returns one stock count.
func (s *Service) GetStockCount(id int) (model.StockCount, error) {
	item, ok := s.StockCounts.Get(id)
	if !ok {
		return model.StockCount{}, notFound("stock count", id)
	}
	return item, nil
}

// ListStockCounts returns every stock count, oldest first.
func (s *Service) ListStockCounts() []model.StockCount {
	return s.StockCounts.List()
}

// UpdateStockCount applies patch to a stock count.
func (s *Service) UpdateStockCount(id int, patch model.StockCountPatch) (model.StockCount, error) {
	current, err := s.GetStockCount(id)
	if err != nil {
		return model.StockCount{}, err
	}
	updated, err := patch.Apply(current)
	if err != nil {
		return model.StockCount{}, err
	}
	if err := s.checkStockCountLinks(updated); err != nil {
		return model.StockCount{}, err
	}
	s.StockCounts.Update(updated)
	return updated, nil
}
