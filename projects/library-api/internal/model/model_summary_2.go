package model

import (
	"cmp"
	"fmt"
)

// Summary is one line for logs and lists.
func (l Loan) Summary() string {
	return fmt.Sprintf("Loan #%d", l.ID)
}

// Map is the record as plain values (for CSV export and templates).
func (l Loan) Map() map[string]any {
	return map[string]any{
		"id":        l.ID,
		"book_id":   l.BookID,
		"member_id": l.MemberID,
		"borrowed":  l.Borrowed,
		"due":       l.Due,
		"renewals":  l.Renewals,
		"status":    string(l.Status),
		"fee":       l.Fee,
	}
}

// CompareLoanByBookID orders loans by book id (for slices.SortFunc).
func CompareLoanByBookID(a, b Loan) int {
	return cmp.Compare(a.BookID, b.BookID)
}

// CompareLoanByMemberID orders loans by member id (for slices.SortFunc).
func CompareLoanByMemberID(a, b Loan) int {
	return cmp.Compare(a.MemberID, b.MemberID)
}

// CompareLoanByBorrowed orders loans by borrowed (for slices.SortFunc).
func CompareLoanByBorrowed(a, b Loan) int {
	return cmp.Compare(a.Borrowed, b.Borrowed)
}

// CompareLoanByDue orders loans by due (for slices.SortFunc).
func CompareLoanByDue(a, b Loan) int {
	return cmp.Compare(a.Due, b.Due)
}

// CompareLoanByRenewals orders loans by renewals (for slices.SortFunc).
func CompareLoanByRenewals(a, b Loan) int {
	return cmp.Compare(a.Renewals, b.Renewals)
}

// CompareLoanByStatus orders loans by status (for slices.SortFunc).
func CompareLoanByStatus(a, b Loan) int {
	return cmp.Compare(string(a.Status), string(b.Status))
}
