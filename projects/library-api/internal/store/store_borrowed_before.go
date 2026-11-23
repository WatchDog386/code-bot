package store

import "library-api/internal/model"

// BorrowedBefore returns records whose borrowed is before day (YYYY-MM-DD).
func (s *LoanStore) BorrowedBefore(day string) []model.Loan {
	return s.Filter(func(item model.Loan) bool { return item.Borrowed < day })
}

// BorrowedAfter returns records whose borrowed is after day (YYYY-MM-DD).
func (s *LoanStore) BorrowedAfter(day string) []model.Loan {
	return s.Filter(func(item model.Loan) bool { return item.Borrowed > day })
}

// BorrowedOn returns records whose borrowed is day.
func (s *LoanStore) BorrowedOn(day string) []model.Loan {
	return s.Filter(func(item model.Loan) bool { return item.Borrowed == day })
}

// DueBefore returns records whose due is before day (YYYY-MM-DD).
func (s *LoanStore) DueBefore(day string) []model.Loan {
	return s.Filter(func(item model.Loan) bool { return item.Due < day })
}

// DueAfter returns records whose due is after day (YYYY-MM-DD).
func (s *LoanStore) DueAfter(day string) []model.Loan {
	return s.Filter(func(item model.Loan) bool { return item.Due > day })
}

// DueOn returns records whose due is day.
func (s *LoanStore) DueOn(day string) []model.Loan {
	return s.Filter(func(item model.Loan) bool { return item.Due == day })
}

// BetweenRenewals returns records whose renewals is within [low, high].
func (s *LoanStore) BetweenRenewals(low, high int) []model.Loan {
	return s.Filter(func(item model.Loan) bool { return item.Renewals >= low && item.Renewals <= high })
}

// TotalRenewals adds up the renewals of every record.
func (s *LoanStore) TotalRenewals() int {
	var total int
	for _, item := range s.List() {
		total += item.Renewals
	}
	return total
}

// AverageRenewals is the mean renewals (0 when there are no records).
func (s *LoanStore) AverageRenewals() float64 {
	items := s.List()
	if len(items) == 0 {
		return 0
	}
	return float64(s.TotalRenewals()) / float64(len(items))
}

// MaxRenewals returns the record with the highest renewals.
func (s *LoanStore) MaxRenewals() (model.Loan, bool) {
	var best model.Loan
	found := false
	for _, item := range s.List() {
		if !found || item.Renewals > best.Renewals {
			best, found = item, true
		}
	}
	return best, found
}

// WithStatus returns records whose status is value.
func (s *LoanStore) WithStatus(value model.LoanStatus) []model.Loan {
	return s.Filter(func(item model.Loan) bool { return item.Status == value })
}
