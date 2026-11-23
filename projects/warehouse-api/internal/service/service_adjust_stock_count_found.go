package service

import "warehouse-api/internal/model"

// AdjustStockCountFound adds delta to the found of a stock count (it can't go below zero).
func (s *Service) AdjustStockCountFound(id int, delta int) (model.StockCount, error) {
	item, err := s.GetStockCount(id)
	if err != nil {
		return model.StockCount{}, err
	}
	value := item.Found + delta
	return s.UpdateStockCount(id, model.StockCountPatch{Found: &value})
}

// StockCountStats sums up every stock count.
type StockCountStats struct {
	Count           int     `json:"count"`
	TotalExpected   int     `json:"total_expected"`
	AverageExpected float64 `json:"average_expected"`
	TotalFound      int     `json:"total_found"`
	AverageFound    float64 `json:"average_found"`
}

// StockCountStats returns totals and breakdowns over every stock count.
func (s *Service) StockCountStats() StockCountStats {
	return StockCountStats{
		Count:           s.StockCounts.Count(),
		TotalExpected:   s.StockCounts.TotalExpected(),
		AverageExpected: s.StockCounts.AverageExpected(),
		TotalFound:      s.StockCounts.TotalFound(),
		AverageFound:    s.StockCounts.AverageFound(),
	}
}
