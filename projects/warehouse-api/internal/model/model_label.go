package model

import (
	"fmt"
	"strings"
)

// Label is a human-friendly name for v.
func (v PurchaseOrderStatus) Label() string {
	text := strings.ReplaceAll(string(v), "_", " ")
	return strings.ToUpper(text[:1]) + text[1:]
}

// ParsePurchaseOrderStatus turns text into a PurchaseOrderStatus.
func ParsePurchaseOrderStatus(text string) (PurchaseOrderStatus, error) {
	v := PurchaseOrderStatus(strings.ToLower(strings.TrimSpace(text)))
	if !v.Valid() {
		return "", Invalid("status", "must be one of %s", PurchaseOrderStatusList())
	}
	return v, nil
}

// PurchaseOrderStatusList is every allowed value, comma separated.
func PurchaseOrderStatusList() string {
	parts := make([]string, len(PurchaseOrderStatusValues))
	for i, v := range PurchaseOrderStatusValues {
		parts[i] = string(v)
	}
	return strings.Join(parts, ", ")
}

// Supplier is a supplier record.
type Supplier struct {
	ID        int    `json:"id"`
	Name      string `json:"name"`
	Email     string `json:"email"`
	Phone     string `json:"phone"`
	Country   string `json:"country"`
	LeadDays  int    `json:"lead_days"`
	Preferred bool   `json:"preferred"`
}

// Validate checks every field and normalises text and amounts in place.
func (s *Supplier) Validate() error {
	var err error
	if s.Name, err = CheckText("name", s.Name, 120, true); err != nil {
		return err
	}
	if s.Email, err = CheckEmail("email", s.Email); err != nil {
		return err
	}
	if s.Phone, err = CheckText("phone", s.Phone, 120, true); err != nil {
		return err
	}
	if s.Country, err = CheckText("country", s.Country, 120, true); err != nil {
		return err
	}
	if err = CheckInt("lead_days", s.LeadDays); err != nil {
		return err
	}
	return nil
}

// Summary is one line for logs and lists.
func (s Supplier) Summary() string {
	return fmt.Sprintf("Supplier #%d: %s", s.ID, s.Name)
}

// Map is the record as plain values (for CSV export and templates).
func (s Supplier) Map() map[string]any {
	return map[string]any{
		"id":        s.ID,
		"name":      s.Name,
		"email":     s.Email,
		"phone":     s.Phone,
		"country":   s.Country,
		"lead_days": s.LeadDays,
		"preferred": s.Preferred,
	}
}
