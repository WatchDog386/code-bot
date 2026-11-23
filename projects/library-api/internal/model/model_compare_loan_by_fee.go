package model

import (
	"cmp"
	"fmt"
)

// CompareLoanByFee orders loans by fee (for slices.SortFunc).
func CompareLoanByFee(a, b Loan) int {
	return cmp.Compare(a.Fee, b.Fee)
}

// LoanPatch changes some fields of a Loan; nil means "leave as it is".
type LoanPatch struct {
	BookID   *int        `json:"book_id,omitempty"`
	MemberID *int        `json:"member_id,omitempty"`
	Borrowed *string     `json:"borrowed,omitempty"`
	Due      *string     `json:"due,omitempty"`
	Renewals *int        `json:"renewals,omitempty"`
	Status   *LoanStatus `json:"status,omitempty"`
	Fee      *float64    `json:"fee,omitempty"`
}

// Apply returns a validated copy of item with the patch applied.
func (p LoanPatch) Apply(item Loan) (Loan, error) {
	if p.BookID != nil {
		item.BookID = *p.BookID
	}
	if p.MemberID != nil {
		item.MemberID = *p.MemberID
	}
	if p.Borrowed != nil {
		item.Borrowed = *p.Borrowed
	}
	if p.Due != nil {
		item.Due = *p.Due
	}
	if p.Renewals != nil {
		item.Renewals = *p.Renewals
	}
	if p.Status != nil {
		item.Status = *p.Status
	}
	if p.Fee != nil {
		item.Fee = *p.Fee
	}
	err := item.Validate()
	return item, err
}

// Reservation is a reservation record.
type Reservation struct {
	ID        int               `json:"id"`
	BookID    int               `json:"book_id"`
	MemberID  int               `json:"member_id"`
	Requested string            `json:"requested"`
	Position  int               `json:"position"`
	Status    ReservationStatus `json:"status"`
	Notes     string            `json:"notes"`
}

// Validate checks every field and normalises text and amounts in place.
func (r *Reservation) Validate() error {
	var err error
	if err = CheckRef("book_id", r.BookID); err != nil {
		return err
	}
	if err = CheckRef("member_id", r.MemberID); err != nil {
		return err
	}
	if err = CheckDate("requested", r.Requested); err != nil {
		return err
	}
	if err = CheckInt("position", r.Position); err != nil {
		return err
	}
	if !r.Status.Valid() {
		return Invalid("status", "must be one of %s", ReservationStatusList())
	}
	if r.Notes, err = CheckText("notes", r.Notes, 2000, false); err != nil {
		return err
	}
	return nil
}

// Summary is one line for logs and lists.
func (r Reservation) Summary() string {
	return fmt.Sprintf("Reservation #%d", r.ID)
}
