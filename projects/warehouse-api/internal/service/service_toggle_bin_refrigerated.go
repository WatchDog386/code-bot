package service

import (
	"fmt"

	"warehouse-api/internal/model"
)

// ToggleBinRefrigerated flips the refrigerated flag of a bin.
func (s *Service) ToggleBinRefrigerated(id int) (model.Bin, error) {
	item, err := s.GetBin(id)
	if err != nil {
		return model.Bin{}, err
	}
	flipped := !item.Refrigerated
	return s.UpdateBin(id, model.BinPatch{Refrigerated: &flipped})
}

// BinStats sums up every bin.
type BinStats struct {
	Count           int     `json:"count"`
	TotalShelf      int     `json:"total_shelf"`
	AverageShelf    float64 `json:"average_shelf"`
	TotalCapacity   int     `json:"total_capacity"`
	AverageCapacity float64 `json:"average_capacity"`
	Refrigerated    int     `json:"refrigerated"`
}

// BinStats returns totals and breakdowns over every bin.
func (s *Service) BinStats() BinStats {
	return BinStats{
		Count:           s.Bins.Count(),
		TotalShelf:      s.Bins.TotalShelf(),
		AverageShelf:    s.Bins.AverageShelf(),
		TotalCapacity:   s.Bins.TotalCapacity(),
		AverageCapacity: s.Bins.AverageCapacity(),
		Refrigerated:    len(s.Bins.WhereRefrigerated(true)),
	}
}

// SampleBin returns valid data for a new bin (links point at seeded records).
func SampleBin(i int) model.Bin {
	return model.Bin{
		Code:         fmt.Sprintf("Bin code %d", i),
		Aisle:        fmt.Sprintf("Bin aisle %d", i),
		Shelf:        i + 1,
		Capacity:     i + 1,
		Refrigerated: i%2 == 1,
	}
}

// CreateStockMovement validates and stores a new stock movement.
func (s *Service) CreateStockMovement(item model.StockMovement) (model.StockMovement, error) {
	item.ID = 0
	if err := item.Validate(); err != nil {
		return model.StockMovement{}, err
	}
	if err := s.checkStockMovementLinks(item); err != nil {
		return model.StockMovement{}, err
	}
	return s.StockMovements.Create(item), nil
}

// GetStockMovement returns one stock movement.
func (s *Service) GetStockMovement(id int) (model.StockMovement, error) {
	item, ok := s.StockMovements.Get(id)
	if !ok {
		return model.StockMovement{}, notFound("stock movement", id)
	}
	return item, nil
}

// ListStockMovements returns every stock movement, oldest first.
func (s *Service) ListStockMovements() []model.StockMovement {
	return s.StockMovements.List()
}
