package service

import (
	"fmt"

	"warehouse-api/internal/model"
)

// StockMovementStats sums up every stock movement.
type StockMovementStats struct {
	Count           int                               `json:"count"`
	TotalQuantity   int                               `json:"total_quantity"`
	AverageQuantity float64                           `json:"average_quantity"`
	ByReason        map[model.StockMovementReason]int `json:"by_reason"`
}

// StockMovementStats returns totals and breakdowns over every stock movement.
func (s *Service) StockMovementStats() StockMovementStats {
	return StockMovementStats{
		Count:           s.StockMovements.Count(),
		TotalQuantity:   s.StockMovements.TotalQuantity(),
		AverageQuantity: s.StockMovements.AverageQuantity(),
		ByReason:        s.StockMovements.CountByReason(),
	}
}

// SampleStockMovement returns valid data for a new stock movement (links point at seeded records).
func SampleStockMovement(i int) model.StockMovement {
	return model.StockMovement{
		ProductID: (i-1)%3 + 1,
		BinID:     (i-1)%3 + 1,
		Quantity:  i + 1,
		Moved:     fmt.Sprintf("2026-%02d-%02d", i%12+1, i%28+1),
		Reason:    model.StockMovementReasonValues[i%5],
		Reference: fmt.Sprintf("Stock movement reference %d", i),
	}
}
