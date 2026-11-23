package model

import (
	"cmp"
	"fmt"
)

// Summary is one line for logs and lists.
func (m Member) Summary() string {
	return fmt.Sprintf("Member #%d: %s", m.ID, m.Name)
}

// Map is the record as plain values (for CSV export and templates).
func (m Member) Map() map[string]any {
	return map[string]any{
		"id":     m.ID,
		"name":   m.Name,
		"email":  m.Email,
		"phone":  m.Phone,
		"joined": m.Joined,
		"tier":   string(m.Tier),
		"fines":  m.Fines,
		"active": m.Active,
	}
}

// CompareMemberByName orders members by name (for slices.SortFunc).
func CompareMemberByName(a, b Member) int {
	return cmp.Compare(a.Name, b.Name)
}

// CompareMemberByEmail orders members by email (for slices.SortFunc).
func CompareMemberByEmail(a, b Member) int {
	return cmp.Compare(a.Email, b.Email)
}

// CompareMemberByPhone orders members by phone (for slices.SortFunc).
func CompareMemberByPhone(a, b Member) int {
	return cmp.Compare(a.Phone, b.Phone)
}

// CompareMemberByJoined orders members by joined (for slices.SortFunc).
func CompareMemberByJoined(a, b Member) int {
	return cmp.Compare(a.Joined, b.Joined)
}

// CompareMemberByTier orders members by tier (for slices.SortFunc).
func CompareMemberByTier(a, b Member) int {
	return cmp.Compare(string(a.Tier), string(b.Tier))
}

// CompareMemberByFines orders members by fines (for slices.SortFunc).
func CompareMemberByFines(a, b Member) int {
	return cmp.Compare(a.Fines, b.Fines)
}

// MemberPatch changes some fields of a Member; nil means "leave as it is".
type MemberPatch struct {
	Name   *string     `json:"name,omitempty"`
	Email  *string     `json:"email,omitempty"`
	Phone  *string     `json:"phone,omitempty"`
	Joined *string     `json:"joined,omitempty"`
	Tier   *MemberTier `json:"tier,omitempty"`
	Fines  *float64    `json:"fines,omitempty"`
	Active *bool       `json:"active,omitempty"`
}
