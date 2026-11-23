package model

import "math"

// Apply returns a validated copy of item with the patch applied.
func (p MemberPatch) Apply(item Member) (Member, error) {
	if p.Name != nil {
		item.Name = *p.Name
	}
	if p.Email != nil {
		item.Email = *p.Email
	}
	if p.Phone != nil {
		item.Phone = *p.Phone
	}
	if p.Joined != nil {
		item.Joined = *p.Joined
	}
	if p.Tier != nil {
		item.Tier = *p.Tier
	}
	if p.Fines != nil {
		item.Fines = *p.Fines
	}
	if p.Active != nil {
		item.Active = *p.Active
	}
	err := item.Validate()
	return item, err
}

// Loan is a loan record.
type Loan struct {
	ID       int        `json:"id"`
	BookID   int        `json:"book_id"`
	MemberID int        `json:"member_id"`
	Borrowed string     `json:"borrowed"`
	Due      string     `json:"due"`
	Renewals int        `json:"renewals"`
	Status   LoanStatus `json:"status"`
	Fee      float64    `json:"fee"`
}

// Validate checks every field and normalises text and amounts in place.
func (l *Loan) Validate() error {
	var err error
	if err = CheckRef("book_id", l.BookID); err != nil {
		return err
	}
	if err = CheckRef("member_id", l.MemberID); err != nil {
		return err
	}
	if err = CheckDate("borrowed", l.Borrowed); err != nil {
		return err
	}
	if err = CheckDate("due", l.Due); err != nil {
		return err
	}
	if err = CheckInt("renewals", l.Renewals); err != nil {
		return err
	}
	if !l.Status.Valid() {
		return Invalid("status", "must be one of %s", LoanStatusList())
	}
	if err = CheckNumber("fee", l.Fee); err != nil {
		return err
	}
	l.Fee = math.Round(l.Fee*100) / 100
	return nil
}
