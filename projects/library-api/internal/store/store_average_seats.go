package store

import (
	"strings"

	"library-api/internal/model"
)

// AverageSeats is the mean seats (0 when there are no records).
func (s *BranchStore) AverageSeats() float64 {
	items := s.List()
	if len(items) == 0 {
		return 0
	}
	return float64(s.TotalSeats()) / float64(len(items))
}

// MaxSeats returns the record with the highest seats.
func (s *BranchStore) MaxSeats() (model.Branch, bool) {
	var best model.Branch
	found := false
	for _, item := range s.List() {
		if !found || item.Seats > best.Seats {
			best, found = item, true
		}
	}
	return best, found
}

// WhereOpenLate returns records whose open late flag equals flag.
func (s *BranchStore) WhereOpenLate(flag bool) []model.Branch {
	return s.Filter(func(item model.Branch) bool { return item.OpenLate == flag })
}

// Search returns records where any text field contains text (any case).
func (s *BranchStore) Search(text string) []model.Branch {
	needle := strings.ToLower(strings.TrimSpace(text))
	return s.Filter(func(item model.Branch) bool {
		for _, value := range []string{item.Name, item.City, item.Phone} {
			if strings.Contains(strings.ToLower(value), needle) {
				return true
			}
		}
		return false
	})
}
