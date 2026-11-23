package model

import (
	"cmp"
	"fmt"
)

// Validate checks every field and normalises text and amounts in place.
func (b *Branch) Validate() error {
	var err error
	if b.Name, err = CheckText("name", b.Name, 120, true); err != nil {
		return err
	}
	if b.City, err = CheckText("city", b.City, 120, true); err != nil {
		return err
	}
	if b.Phone, err = CheckText("phone", b.Phone, 120, true); err != nil {
		return err
	}
	if err = CheckDate("opened", b.Opened); err != nil {
		return err
	}
	if err = CheckInt("seats", b.Seats); err != nil {
		return err
	}
	return nil
}

// Summary is one line for logs and lists.
func (b Branch) Summary() string {
	return fmt.Sprintf("Branch #%d: %s", b.ID, b.Name)
}

// Map is the record as plain values (for CSV export and templates).
func (b Branch) Map() map[string]any {
	return map[string]any{
		"id":        b.ID,
		"name":      b.Name,
		"city":      b.City,
		"phone":     b.Phone,
		"opened":    b.Opened,
		"seats":     b.Seats,
		"open_late": b.OpenLate,
	}
}

// CompareBranchByName orders branches by name (for slices.SortFunc).
func CompareBranchByName(a, b Branch) int {
	return cmp.Compare(a.Name, b.Name)
}

// CompareBranchByCity orders branches by city (for slices.SortFunc).
func CompareBranchByCity(a, b Branch) int {
	return cmp.Compare(a.City, b.City)
}

// CompareBranchByPhone orders branches by phone (for slices.SortFunc).
func CompareBranchByPhone(a, b Branch) int {
	return cmp.Compare(a.Phone, b.Phone)
}

// CompareBranchByOpened orders branches by opened (for slices.SortFunc).
func CompareBranchByOpened(a, b Branch) int {
	return cmp.Compare(a.Opened, b.Opened)
}

// CompareBranchBySeats orders branches by seats (for slices.SortFunc).
func CompareBranchBySeats(a, b Branch) int {
	return cmp.Compare(a.Seats, b.Seats)
}
