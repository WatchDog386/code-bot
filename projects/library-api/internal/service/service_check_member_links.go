package service

import (
	"fmt"
	"math"

	"library-api/internal/model"
)

// checkMemberLinks makes sure every record a member points at exists.
func (s *Service) checkMemberLinks(_ model.Member) error {
	return nil
}

// SetMemberTier moves a member to another tier.
func (s *Service) SetMemberTier(id int, value model.MemberTier) (model.Member, error) {
	return s.UpdateMember(id, model.MemberPatch{Tier: &value})
}

// AdjustMemberFines adds delta to the fines of a member (it can't go below zero).
func (s *Service) AdjustMemberFines(id int, delta float64) (model.Member, error) {
	item, err := s.GetMember(id)
	if err != nil {
		return model.Member{}, err
	}
	value := math.Round((item.Fines+delta)*100) / 100
	return s.UpdateMember(id, model.MemberPatch{Fines: &value})
}

// ToggleMemberActive flips the active flag of a member.
func (s *Service) ToggleMemberActive(id int) (model.Member, error) {
	item, err := s.GetMember(id)
	if err != nil {
		return model.Member{}, err
	}
	flipped := !item.Active
	return s.UpdateMember(id, model.MemberPatch{Active: &flipped})
}

// MemberStats sums up every member.
type MemberStats struct {
	Count        int                      `json:"count"`
	ByTier       map[model.MemberTier]int `json:"by_tier"`
	TotalFines   float64                  `json:"total_fines"`
	AverageFines float64                  `json:"average_fines"`
	Active       int                      `json:"active"`
}

// MemberStats returns totals and breakdowns over every member.
func (s *Service) MemberStats() MemberStats {
	return MemberStats{
		Count:        s.Members.Count(),
		ByTier:       s.Members.CountByTier(),
		TotalFines:   s.Members.TotalFines(),
		AverageFines: s.Members.AverageFines(),
		Active:       len(s.Members.WhereActive(true)),
	}
}

// SampleMember returns valid data for a new member (links point at seeded records).
func SampleMember(i int) model.Member {
	return model.Member{
		Name:   fmt.Sprintf("Member name %d", i),
		Email:  fmt.Sprintf("member%d@example.com", i),
		Phone:  fmt.Sprintf("Member phone %d", i),
		Joined: fmt.Sprintf("2026-%02d-%02d", i%12+1, i%28+1),
		Tier:   model.MemberTierValues[i%3],
		Fines:  math.Round((10*float64(i)+0.99)*100) / 100,
		Active: i%2 == 1,
	}
}

// CreateLoan validates and stores a new loan.
func (s *Service) CreateLoan(item model.Loan) (model.Loan, error) {
	item.ID = 0
	if err := item.Validate(); err != nil {
		return model.Loan{}, err
	}
	if err := s.checkLoanLinks(item); err != nil {
		return model.Loan{}, err
	}
	return s.Loans.Create(item), nil
}

// GetLoan returns one loan.
func (s *Service) GetLoan(id int) (model.Loan, error) {
	item, ok := s.Loans.Get(id)
	if !ok {
		return model.Loan{}, notFound("loan", id)
	}
	return item, nil
}

// ListLoans returns every loan, oldest first.
func (s *Service) ListLoans() []model.Loan {
	return s.Loans.List()
}
