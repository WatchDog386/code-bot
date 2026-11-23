package store

import (
	"strings"

	"library-api/internal/model"
)

// FindByPhone returns records whose phone is exactly value.
func (s *BranchStore) FindByPhone(value string) []model.Branch {
	return s.Filter(func(item model.Branch) bool { return item.Phone == value })
}

// SearchPhone returns records whose phone contains text (any case).
func (s *BranchStore) SearchPhone(text string) []model.Branch {
	needle := strings.ToLower(strings.TrimSpace(text))
	return s.Filter(func(item model.Branch) bool { return strings.Contains(strings.ToLower(item.Phone), needle) })
}

// OpenedBefore returns records whose opened is before day (YYYY-MM-DD).
func (s *BranchStore) OpenedBefore(day string) []model.Branch {
	return s.Filter(func(item model.Branch) bool { return item.Opened < day })
}

// OpenedAfter returns records whose opened is after day (YYYY-MM-DD).
func (s *BranchStore) OpenedAfter(day string) []model.Branch {
	return s.Filter(func(item model.Branch) bool { return item.Opened > day })
}

// OpenedOn returns records whose opened is day.
func (s *BranchStore) OpenedOn(day string) []model.Branch {
	return s.Filter(func(item model.Branch) bool { return item.Opened == day })
}

// BetweenSeats returns records whose seats is within [low, high].
func (s *BranchStore) BetweenSeats(low, high int) []model.Branch {
	return s.Filter(func(item model.Branch) bool { return item.Seats >= low && item.Seats <= high })
}

// TotalSeats adds up the seats of every record.
func (s *BranchStore) TotalSeats() int {
	var total int
	for _, item := range s.List() {
		total += item.Seats
	}
	return total
}
