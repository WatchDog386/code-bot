package model

// Apply returns a validated copy of item with the patch applied.
func (p SupplierPatch) Apply(item Supplier) (Supplier, error) {
	if p.Name != nil {
		item.Name = *p.Name
	}
	if p.Email != nil {
		item.Email = *p.Email
	}
	if p.Phone != nil {
		item.Phone = *p.Phone
	}
	if p.Country != nil {
		item.Country = *p.Country
	}
	if p.LeadDays != nil {
		item.LeadDays = *p.LeadDays
	}
	if p.Preferred != nil {
		item.Preferred = *p.Preferred
	}
	err := item.Validate()
	return item, err
}

// Product is a product record.
type Product struct {
	ID           int             `json:"id"`
	SupplierID   int             `json:"supplier_id"`
	Sku          string          `json:"sku"`
	Name         string          `json:"name"`
	UnitCost     float64         `json:"unit_cost"`
	UnitPrice    float64         `json:"unit_price"`
	ReorderLevel int             `json:"reorder_level"`
	Category     ProductCategory `json:"category"`
	Active       bool            `json:"active"`
}
