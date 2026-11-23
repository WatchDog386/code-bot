package service

import (
	"fmt"

	"library-api/internal/model"
)

// BranchStats returns totals and breakdowns over every branch.
func (s *Service) BranchStats() BranchStats {
	return BranchStats{
		Count:        s.Branches.Count(),
		TotalSeats:   s.Branches.TotalSeats(),
		AverageSeats: s.Branches.AverageSeats(),
		OpenLate:     len(s.Branches.WhereOpenLate(true)),
	}
}

// SampleBranch returns valid data for a new branch (links point at seeded records).
func SampleBranch(i int) model.Branch {
	return model.Branch{
		Name:     fmt.Sprintf("Branch name %d", i),
		City:     fmt.Sprintf("Branch city %d", i),
		Phone:    fmt.Sprintf("Branch phone %d", i),
		Opened:   fmt.Sprintf("2026-%02d-%02d", i%12+1, i%28+1),
		Seats:    i + 1,
		OpenLate: i%2 == 1,
	}
}
