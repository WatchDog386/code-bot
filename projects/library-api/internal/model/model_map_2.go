package model

import "cmp"

// Map is the record as plain values (for CSV export and templates).
func (r Reservation) Map() map[string]any {
	return map[string]any{
		"id":        r.ID,
		"book_id":   r.BookID,
		"member_id": r.MemberID,
		"requested": r.Requested,
		"position":  r.Position,
		"status":    string(r.Status),
		"notes":     r.Notes,
	}
}

// CompareReservationByBookID orders reservations by book id (for slices.SortFunc).
func CompareReservationByBookID(a, b Reservation) int {
	return cmp.Compare(a.BookID, b.BookID)
}

// CompareReservationByMemberID orders reservations by member id (for slices.SortFunc).
func CompareReservationByMemberID(a, b Reservation) int {
	return cmp.Compare(a.MemberID, b.MemberID)
}

// CompareReservationByRequested orders reservations by requested (for slices.SortFunc).
func CompareReservationByRequested(a, b Reservation) int {
	return cmp.Compare(a.Requested, b.Requested)
}

// CompareReservationByPosition orders reservations by position (for slices.SortFunc).
func CompareReservationByPosition(a, b Reservation) int {
	return cmp.Compare(a.Position, b.Position)
}

// CompareReservationByStatus orders reservations by status (for slices.SortFunc).
func CompareReservationByStatus(a, b Reservation) int {
	return cmp.Compare(string(a.Status), string(b.Status))
}

// CompareReservationByNotes orders reservations by notes (for slices.SortFunc).
func CompareReservationByNotes(a, b Reservation) int {
	return cmp.Compare(a.Notes, b.Notes)
}

// ReservationPatch changes some fields of a Reservation; nil means "leave as it is".
type ReservationPatch struct {
	BookID    *int               `json:"book_id,omitempty"`
	MemberID  *int               `json:"member_id,omitempty"`
	Requested *string            `json:"requested,omitempty"`
	Position  *int               `json:"position,omitempty"`
	Status    *ReservationStatus `json:"status,omitempty"`
	Notes     *string            `json:"notes,omitempty"`
}
