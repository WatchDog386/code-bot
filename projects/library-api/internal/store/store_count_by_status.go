package store

import "library-api/internal/model"

// CountByStatus counts records for every status.
func (s *LoanStore) CountByStatus() map[model.LoanStatus]int {
	counts := map[model.LoanStatus]int{}
	for _, v := range model.LoanStatusValues {
		counts[v] = 0
	}
	for _, item := range s.List() {
		counts[item.Status]++
	}
	return counts
}

// BetweenFee returns records whose fee is within [low, high].
func (s *LoanStore) BetweenFee(low, high float64) []model.Loan {
	return s.Filter(func(item model.Loan) bool { return item.Fee >= low && item.Fee <= high })
}

// TotalFee adds up the fee of every record.
func (s *LoanStore) TotalFee() float64 {
	var total float64
	for _, item := range s.List() {
		total += item.Fee
	}
	return total
}

// AverageFee is the mean fee (0 when there are no records).
func (s *LoanStore) AverageFee() float64 {
	items := s.List()
	if len(items) == 0 {
		return 0
	}
	return float64(s.TotalFee()) / float64(len(items))
}
