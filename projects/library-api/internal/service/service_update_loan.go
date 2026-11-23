package service

import (
	"math"

	"library-api/internal/model"
)

// UpdateLoan applies patch to a loan.
func (s *Service) UpdateLoan(id int, patch model.LoanPatch) (model.Loan, error) {
	current, err := s.GetLoan(id)
	if err != nil {
		return model.Loan{}, err
	}
	updated, err := patch.Apply(current)
	if err != nil {
		return model.Loan{}, err
	}
	if err := s.checkLoanLinks(updated); err != nil {
		return model.Loan{}, err
	}
	s.Loans.Update(updated)
	return updated, nil
}

// DeleteLoan removes a loan nothing points at any more.
func (s *Service) DeleteLoan(id int) error {
	if _, err := s.GetLoan(id); err != nil {
		return err
	}
	s.Loans.Delete(id)
	return nil
}

// checkLoanLinks makes sure every record a loan points at exists.
func (s *Service) checkLoanLinks(item model.Loan) error {
	if _, ok := s.Books.Get(item.BookID); !ok {
		return notFound("book", item.BookID)
	}
	if _, ok := s.Members.Get(item.MemberID); !ok {
		return notFound("member", item.MemberID)
	}
	return nil
}

// AdjustLoanRenewals adds delta to the renewals of a loan (it can't go below zero).
func (s *Service) AdjustLoanRenewals(id int, delta int) (model.Loan, error) {
	item, err := s.GetLoan(id)
	if err != nil {
		return model.Loan{}, err
	}
	value := item.Renewals + delta
	return s.UpdateLoan(id, model.LoanPatch{Renewals: &value})
}

// SetLoanStatus moves a loan to another status.
func (s *Service) SetLoanStatus(id int, value model.LoanStatus) (model.Loan, error) {
	return s.UpdateLoan(id, model.LoanPatch{Status: &value})
}

// AdjustLoanFee adds delta to the fee of a loan (it can't go below zero).
func (s *Service) AdjustLoanFee(id int, delta float64) (model.Loan, error) {
	item, err := s.GetLoan(id)
	if err != nil {
		return model.Loan{}, err
	}
	value := math.Round((item.Fee+delta)*100) / 100
	return s.UpdateLoan(id, model.LoanPatch{Fee: &value})
}
