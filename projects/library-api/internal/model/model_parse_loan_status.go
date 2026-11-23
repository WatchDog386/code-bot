package model

import "strings"

// ParseLoanStatus turns text into a LoanStatus.
func ParseLoanStatus(text string) (LoanStatus, error) {
	v := LoanStatus(strings.ToLower(strings.TrimSpace(text)))
	if !v.Valid() {
		return "", Invalid("status", "must be one of %s", LoanStatusList())
	}
	return v, nil
}

// LoanStatusList is every allowed value, comma separated.
func LoanStatusList() string {
	parts := make([]string, len(LoanStatusValues))
	for i, v := range LoanStatusValues {
		parts[i] = string(v)
	}
	return strings.Join(parts, ", ")
}

// ReservationStatus is the status of a Reservation.
type ReservationStatus string

// Allowed ReservationStatus values.
const (
	ReservationStatusWaiting   ReservationStatus = "waiting"
	ReservationStatusReady     ReservationStatus = "ready"
	ReservationStatusCancelled ReservationStatus = "cancelled"
	ReservationStatusFulfilled ReservationStatus = "fulfilled"
)

// ReservationStatusValues lists every allowed ReservationStatus.
var ReservationStatusValues = []ReservationStatus{ReservationStatusWaiting, ReservationStatusReady, ReservationStatusCancelled, ReservationStatusFulfilled}

// Valid reports whether v is one of the allowed values.
func (v ReservationStatus) Valid() bool {
	for _, allowed := range ReservationStatusValues {
		if v == allowed {
			return true
		}
	}
	return false
}

// Label is a human-friendly name for v.
func (v ReservationStatus) Label() string {
	text := strings.ReplaceAll(string(v), "_", " ")
	return strings.ToUpper(text[:1]) + text[1:]
}

// ParseReservationStatus turns text into a ReservationStatus.
func ParseReservationStatus(text string) (ReservationStatus, error) {
	v := ReservationStatus(strings.ToLower(strings.TrimSpace(text)))
	if !v.Valid() {
		return "", Invalid("status", "must be one of %s", ReservationStatusList())
	}
	return v, nil
}

// ReservationStatusList is every allowed value, comma separated.
func ReservationStatusList() string {
	parts := make([]string, len(ReservationStatusValues))
	for i, v := range ReservationStatusValues {
		parts[i] = string(v)
	}
	return strings.Join(parts, ", ")
}

// Author is a author record.
type Author struct {
	ID      int    `json:"id"`
	Name    string `json:"name"`
	Email   string `json:"email"`
	Country string `json:"country"`
	Born    string `json:"born"`
	Active  bool   `json:"active"`
}
