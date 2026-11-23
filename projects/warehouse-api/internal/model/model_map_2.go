package model

import "cmp"

// Map is the record as plain values (for CSV export and templates).
func (b Bin) Map() map[string]any {
	return map[string]any{
		"id":           b.ID,
		"code":         b.Code,
		"aisle":        b.Aisle,
		"shelf":        b.Shelf,
		"capacity":     b.Capacity,
		"refrigerated": b.Refrigerated,
	}
}

// CompareBinByCode orders bins by code (for slices.SortFunc).
func CompareBinByCode(a, b Bin) int {
	return cmp.Compare(a.Code, b.Code)
}

// CompareBinByAisle orders bins by aisle (for slices.SortFunc).
func CompareBinByAisle(a, b Bin) int {
	return cmp.Compare(a.Aisle, b.Aisle)
}

// CompareBinByShelf orders bins by shelf (for slices.SortFunc).
func CompareBinByShelf(a, b Bin) int {
	return cmp.Compare(a.Shelf, b.Shelf)
}

// CompareBinByCapacity orders bins by capacity (for slices.SortFunc).
func CompareBinByCapacity(a, b Bin) int {
	return cmp.Compare(a.Capacity, b.Capacity)
}

// BinPatch changes some fields of a Bin; nil means "leave as it is".
type BinPatch struct {
	Code         *string `json:"code,omitempty"`
	Aisle        *string `json:"aisle,omitempty"`
	Shelf        *int    `json:"shelf,omitempty"`
	Capacity     *int    `json:"capacity,omitempty"`
	Refrigerated *bool   `json:"refrigerated,omitempty"`
}

// Apply returns a validated copy of item with the patch applied.
func (p BinPatch) Apply(item Bin) (Bin, error) {
	if p.Code != nil {
		item.Code = *p.Code
	}
	if p.Aisle != nil {
		item.Aisle = *p.Aisle
	}
	if p.Shelf != nil {
		item.Shelf = *p.Shelf
	}
	if p.Capacity != nil {
		item.Capacity = *p.Capacity
	}
	if p.Refrigerated != nil {
		item.Refrigerated = *p.Refrigerated
	}
	err := item.Validate()
	return item, err
}

// StockMovement is a stock movement record.
type StockMovement struct {
	ID        int                 `json:"id"`
	ProductID int                 `json:"product_id"`
	BinID     int                 `json:"bin_id"`
	Quantity  int                 `json:"quantity"`
	Moved     string              `json:"moved"`
	Reason    StockMovementReason `json:"reason"`
	Reference string              `json:"reference"`
}
