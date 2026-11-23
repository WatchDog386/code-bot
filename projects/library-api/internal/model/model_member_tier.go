package model

import "strings"

// MemberTier is the tier of a Member.
type MemberTier string

// Allowed MemberTier values.
const (
	MemberTierBasic   MemberTier = "basic"
	MemberTierStudent MemberTier = "student"
	MemberTierPremium MemberTier = "premium"
)

// MemberTierValues lists every allowed MemberTier.
var MemberTierValues = []MemberTier{MemberTierBasic, MemberTierStudent, MemberTierPremium}

// Valid reports whether v is one of the allowed values.
func (v MemberTier) Valid() bool {
	for _, allowed := range MemberTierValues {
		if v == allowed {
			return true
		}
	}
	return false
}

// Label is a human-friendly name for v.
func (v MemberTier) Label() string {
	text := strings.ReplaceAll(string(v), "_", " ")
	return strings.ToUpper(text[:1]) + text[1:]
}

// ParseMemberTier turns text into a MemberTier.
func ParseMemberTier(text string) (MemberTier, error) {
	v := MemberTier(strings.ToLower(strings.TrimSpace(text)))
	if !v.Valid() {
		return "", Invalid("tier", "must be one of %s", MemberTierList())
	}
	return v, nil
}

// MemberTierList is every allowed value, comma separated.
func MemberTierList() string {
	parts := make([]string, len(MemberTierValues))
	for i, v := range MemberTierValues {
		parts[i] = string(v)
	}
	return strings.Join(parts, ", ")
}

// LoanStatus is the status of a Loan.
type LoanStatus string

// Allowed LoanStatus values.
const (
	LoanStatusOpen     LoanStatus = "open"
	LoanStatusReturned LoanStatus = "returned"
	LoanStatusOverdue  LoanStatus = "overdue"
	LoanStatusLost     LoanStatus = "lost"
)

// LoanStatusValues lists every allowed LoanStatus.
var LoanStatusValues = []LoanStatus{LoanStatusOpen, LoanStatusReturned, LoanStatusOverdue, LoanStatusLost}

// Valid reports whether v is one of the allowed values.
func (v LoanStatus) Valid() bool {
	for _, allowed := range LoanStatusValues {
		if v == allowed {
			return true
		}
	}
	return false
}

// Label is a human-friendly name for v.
func (v LoanStatus) Label() string {
	text := strings.ReplaceAll(string(v), "_", " ")
	return strings.ToUpper(text[:1]) + text[1:]
}
