package store

import (
	"strings"
	"sync"

	"library-api/internal/model"
)

// CountByTier counts records for every tier.
func (s *MemberStore) CountByTier() map[model.MemberTier]int {
	counts := map[model.MemberTier]int{}
	for _, v := range model.MemberTierValues {
		counts[v] = 0
	}
	for _, item := range s.List() {
		counts[item.Tier]++
	}
	return counts
}

// BetweenFines returns records whose fines is within [low, high].
func (s *MemberStore) BetweenFines(low, high float64) []model.Member {
	return s.Filter(func(item model.Member) bool { return item.Fines >= low && item.Fines <= high })
}

// TotalFines adds up the fines of every record.
func (s *MemberStore) TotalFines() float64 {
	var total float64
	for _, item := range s.List() {
		total += item.Fines
	}
	return total
}

// AverageFines is the mean fines (0 when there are no records).
func (s *MemberStore) AverageFines() float64 {
	items := s.List()
	if len(items) == 0 {
		return 0
	}
	return float64(s.TotalFines()) / float64(len(items))
}

// MaxFines returns the record with the highest fines.
func (s *MemberStore) MaxFines() (model.Member, bool) {
	var best model.Member
	found := false
	for _, item := range s.List() {
		if !found || item.Fines > best.Fines {
			best, found = item, true
		}
	}
	return best, found
}

// WhereActive returns records whose active flag equals flag.
func (s *MemberStore) WhereActive(flag bool) []model.Member {
	return s.Filter(func(item model.Member) bool { return item.Active == flag })
}

// Search returns records where any text field contains text (any case).
func (s *MemberStore) Search(text string) []model.Member {
	needle := strings.ToLower(strings.TrimSpace(text))
	return s.Filter(func(item model.Member) bool {
		for _, value := range []string{item.Name, item.Email, item.Phone} {
			if strings.Contains(strings.ToLower(value), needle) {
				return true
			}
		}
		return false
	})
}

// LoanStore keeps every loan.
type LoanStore struct {
	mu     sync.RWMutex
	items  map[int]model.Loan
	nextID int
}

// NewLoanStore returns an empty store.
func NewLoanStore() *LoanStore {
	return &LoanStore{items: map[int]model.Loan{}, nextID: 1}
}
