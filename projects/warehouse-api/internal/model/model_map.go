package model

import "cmp"

// Map is the record as plain values (for CSV export and templates).
func (p Product) Map() map[string]any {
	return map[string]any{
		"id":            p.ID,
		"supplier_id":   p.SupplierID,
		"sku":           p.Sku,
		"name":          p.Name,
		"unit_cost":     p.UnitCost,
		"unit_price":    p.UnitPrice,
		"reorder_level": p.ReorderLevel,
		"category":      string(p.Category),
		"active":        p.Active,
	}
}

// CompareProductBySupplierID orders products by supplier id (for slices.SortFunc).
func CompareProductBySupplierID(a, b Product) int {
	return cmp.Compare(a.SupplierID, b.SupplierID)
}

// CompareProductBySku orders products by sku (for slices.SortFunc).
func CompareProductBySku(a, b Product) int {
	return cmp.Compare(a.Sku, b.Sku)
}

// CompareProductByName orders products by name (for slices.SortFunc).
func CompareProductByName(a, b Product) int {
	return cmp.Compare(a.Name, b.Name)
}

// CompareProductByUnitCost orders products by unit cost (for slices.SortFunc).
func CompareProductByUnitCost(a, b Product) int {
	return cmp.Compare(a.UnitCost, b.UnitCost)
}

// CompareProductByUnitPrice orders products by unit price (for slices.SortFunc).
func CompareProductByUnitPrice(a, b Product) int {
	return cmp.Compare(a.UnitPrice, b.UnitPrice)
}

// CompareProductByReorderLevel orders products by reorder level (for slices.SortFunc).
func CompareProductByReorderLevel(a, b Product) int {
	return cmp.Compare(a.ReorderLevel, b.ReorderLevel)
}

// CompareProductByCategory orders products by category (for slices.SortFunc).
func CompareProductByCategory(a, b Product) int {
	return cmp.Compare(string(a.Category), string(b.Category))
}

// ProductPatch changes some fields of a Product; nil means "leave as it is".
type ProductPatch struct {
	SupplierID   *int             `json:"supplier_id,omitempty"`
	Sku          *string          `json:"sku,omitempty"`
	Name         *string          `json:"name,omitempty"`
	UnitCost     *float64         `json:"unit_cost,omitempty"`
	UnitPrice    *float64         `json:"unit_price,omitempty"`
	ReorderLevel *int             `json:"reorder_level,omitempty"`
	Category     *ProductCategory `json:"category,omitempty"`
	Active       *bool            `json:"active,omitempty"`
}
