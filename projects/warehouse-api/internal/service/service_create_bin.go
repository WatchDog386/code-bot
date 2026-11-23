package service

import "warehouse-api/internal/model"

// CreateBin validates and stores a new bin.
func (s *Service) CreateBin(item model.Bin) (model.Bin, error) {
	item.ID = 0
	if err := item.Validate(); err != nil {
		return model.Bin{}, err
	}
	if err := s.checkBinLinks(item); err != nil {
		return model.Bin{}, err
	}
	return s.Bins.Create(item), nil
}

// GetBin returns one bin.
func (s *Service) GetBin(id int) (model.Bin, error) {
	item, ok := s.Bins.Get(id)
	if !ok {
		return model.Bin{}, notFound("bin", id)
	}
	return item, nil
}

// ListBins returns every bin, oldest first.
func (s *Service) ListBins() []model.Bin {
	return s.Bins.List()
}

// UpdateBin applies patch to a bin.
func (s *Service) UpdateBin(id int, patch model.BinPatch) (model.Bin, error) {
	current, err := s.GetBin(id)
	if err != nil {
		return model.Bin{}, err
	}
	updated, err := patch.Apply(current)
	if err != nil {
		return model.Bin{}, err
	}
	if err := s.checkBinLinks(updated); err != nil {
		return model.Bin{}, err
	}
	s.Bins.Update(updated)
	return updated, nil
}

// DeleteBin removes a bin nothing points at any more.
func (s *Service) DeleteBin(id int) error {
	if _, err := s.GetBin(id); err != nil {
		return err
	}
	if n := s.StockMovements.CountForBin(id); n > 0 {
		return inUse("bin", id, n, "stock movements")
	}
	if n := s.StockCounts.CountForBin(id); n > 0 {
		return inUse("bin", id, n, "stock counts")
	}
	s.Bins.Delete(id)
	return nil
}

// checkBinLinks makes sure every record a bin points at exists.
func (s *Service) checkBinLinks(_ model.Bin) error {
	return nil
}

// AdjustBinShelf adds delta to the shelf of a bin (it can't go below zero).
func (s *Service) AdjustBinShelf(id int, delta int) (model.Bin, error) {
	item, err := s.GetBin(id)
	if err != nil {
		return model.Bin{}, err
	}
	value := item.Shelf + delta
	return s.UpdateBin(id, model.BinPatch{Shelf: &value})
}

// AdjustBinCapacity adds delta to the capacity of a bin (it can't go below zero).
func (s *Service) AdjustBinCapacity(id int, delta int) (model.Bin, error) {
	item, err := s.GetBin(id)
	if err != nil {
		return model.Bin{}, err
	}
	value := item.Capacity + delta
	return s.UpdateBin(id, model.BinPatch{Capacity: &value})
}
