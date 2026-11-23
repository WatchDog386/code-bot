package model

import "cmp"

// CompareSupplierByName orders suppliers by name (for slices.SortFunc).
func CompareSupplierByName(a, b Supplier) int {
	return cmp.Compare(a.Name, b.Name)
}

// CompareSupplierByEmail orders suppliers by email (for slices.SortFunc).
func CompareSupplierByEmail(a, b Supplier) int {
	return cmp.Compare(a.Email, b.Email)
}

// CompareSupplierByPhone orders suppliers by phone (for slices.SortFunc).
func CompareSupplierByPhone(a, b Supplier) int {
	return cmp.Compare(a.Phone, b.Phone)
}

// CompareSupplierByCountry orders suppliers by country (for slices.SortFunc).
func CompareSupplierByCountry(a, b Supplier) int {
	return cmp.Compare(a.Country, b.Country)
}

// CompareSupplierByLeadDays orders suppliers by lead days (for slices.SortFunc).
func CompareSupplierByLeadDays(a, b Supplier) int {
	return cmp.Compare(a.LeadDays, b.LeadDays)
}

// SupplierPatch changes some fields of a Supplier; nil means "leave as it is".
type SupplierPatch struct {
	Name      *string `json:"name,omitempty"`
	Email     *string `json:"email,omitempty"`
	Phone     *string `json:"phone,omitempty"`
	Country   *string `json:"country,omitempty"`
	LeadDays  *int    `json:"lead_days,omitempty"`
	Preferred *bool   `json:"preferred,omitempty"`
}
