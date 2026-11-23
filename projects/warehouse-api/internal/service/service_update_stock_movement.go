package service

import "warehouse-api/internal/model"

// UpdateStockMovement applies patch to a stock movement.
func (s *Service) UpdateStockMovement(id int, patch model.StockMovementPatch) (model.StockMovement, error) {
	current, err := s.GetStockMovement(id)
	if err != nil {
		return model.StockMovement{}, err
	}
	updated, err := patch.Apply(current)
	if err != nil {
		return model.StockMovement{}, err
	}
	if err := s.checkStockMovementLinks(updated); err != nil {
		return model.StockMovement{}, err
	}
	s.StockMovements.Update(updated)
	return updated, nil
}

// DeleteStockMovement removes a stock movement nothing points at any more.
func (s *Service) DeleteStockMovement(id int) error {
	if _, err := s.GetStockMovement(id); err != nil {
		return err
	}
	s.StockMovements.Delete(id)
	return nil
}

// checkStockMovementLinks makes sure every record a stock movement points at exists.
func (s *Service) checkStockMovementLinks(item model.StockMovement) error {
	if _, ok := s.Products.Get(item.ProductID); !ok {
		return notFound("product", item.ProductID)
	}
	if _, ok := s.Bins.Get(item.BinID); !ok {
		return notFound("bin", item.BinID)
	}
	return nil
}

// AdjustStockMovementQuantity adds delta to the quantity of a stock movement (it can't go below zero).
func (s *Service) AdjustStockMovementQuantity(id int, delta int) (model.StockMovement, error) {
	item, err := s.GetStockMovement(id)
	if err != nil {
		return model.StockMovement{}, err
	}
	value := item.Quantity + delta
	return s.UpdateStockMovement(id, model.StockMovementPatch{Quantity: &value})
}

// SetStockMovementReason moves a stock movement to another reason.
func (s *Service) SetStockMovementReason(id int, value model.StockMovementReason) (model.StockMovement, error) {
	return s.UpdateStockMovement(id, model.StockMovementPatch{Reason: &value})
}
