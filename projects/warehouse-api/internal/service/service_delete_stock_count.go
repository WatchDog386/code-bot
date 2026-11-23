package service

import "warehouse-api/internal/model"

// DeleteStockCount removes a stock count nothing points at any more.
func (s *Service) DeleteStockCount(id int) error {
	if _, err := s.GetStockCount(id); err != nil {
		return err
	}
	s.StockCounts.Delete(id)
	return nil
}

// checkStockCountLinks makes sure every record a stock count points at exists.
func (s *Service) checkStockCountLinks(item model.StockCount) error {
	if _, ok := s.Bins.Get(item.BinID); !ok {
		return notFound("bin", item.BinID)
	}
	if _, ok := s.Products.Get(item.ProductID); !ok {
		return notFound("product", item.ProductID)
	}
	return nil
}

// AdjustStockCountExpected adds delta to the expected of a stock count (it can't go below zero).
func (s *Service) AdjustStockCountExpected(id int, delta int) (model.StockCount, error) {
	item, err := s.GetStockCount(id)
	if err != nil {
		return model.StockCount{}, err
	}
	value := item.Expected + delta
	return s.UpdateStockCount(id, model.StockCountPatch{Expected: &value})
}
