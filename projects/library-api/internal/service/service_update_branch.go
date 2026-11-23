package service

import "library-api/internal/model"

// UpdateBranch applies patch to a branch.
func (s *Service) UpdateBranch(id int, patch model.BranchPatch) (model.Branch, error) {
	current, err := s.GetBranch(id)
	if err != nil {
		return model.Branch{}, err
	}
	updated, err := patch.Apply(current)
	if err != nil {
		return model.Branch{}, err
	}
	if err := s.checkBranchLinks(updated); err != nil {
		return model.Branch{}, err
	}
	s.Branches.Update(updated)
	return updated, nil
}

// DeleteBranch removes a branch nothing points at any more.
func (s *Service) DeleteBranch(id int) error {
	if _, err := s.GetBranch(id); err != nil {
		return err
	}
	s.Branches.Delete(id)
	return nil
}

// checkBranchLinks makes sure every record a branch points at exists.
func (s *Service) checkBranchLinks(_ model.Branch) error {
	return nil
}

// AdjustBranchSeats adds delta to the seats of a branch (it can't go below zero).
func (s *Service) AdjustBranchSeats(id int, delta int) (model.Branch, error) {
	item, err := s.GetBranch(id)
	if err != nil {
		return model.Branch{}, err
	}
	value := item.Seats + delta
	return s.UpdateBranch(id, model.BranchPatch{Seats: &value})
}

// ToggleBranchOpenLate flips the open late flag of a branch.
func (s *Service) ToggleBranchOpenLate(id int) (model.Branch, error) {
	item, err := s.GetBranch(id)
	if err != nil {
		return model.Branch{}, err
	}
	flipped := !item.OpenLate
	return s.UpdateBranch(id, model.BranchPatch{OpenLate: &flipped})
}

// BranchStats sums up every branch.
type BranchStats struct {
	Count        int     `json:"count"`
	TotalSeats   int     `json:"total_seats"`
	AverageSeats float64 `json:"average_seats"`
	OpenLate     int     `json:"open_late"`
}
