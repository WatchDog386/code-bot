package model

import "cmp"

// CompareStockMovementByReference orders stock movements by reference (for slices.SortFunc).
func CompareStockMovementByReference(a, b StockMovement) int {
	return cmp.Compare(a.Reference, b.Reference)
}

// StockMovementPatch changes some fields of a StockMovement; nil means "leave as it is".
type StockMovementPatch struct {
	ProductID *int                 `json:"product_id,omitempty"`
	BinID     *int                 `json:"bin_id,omitempty"`
	Quantity  *int                 `json:"quantity,omitempty"`
	Moved     *string              `json:"moved,omitempty"`
	Reason    *StockMovementReason `json:"reason,omitempty"`
	Reference *string              `json:"reference,omitempty"`
}

// Apply returns a validated copy of item with the patch applied.
func (p StockMovementPatch) Apply(item StockMovement) (StockMovement, error) {
	if p.ProductID != nil {
		item.ProductID = *p.ProductID
	}
	if p.BinID != nil {
		item.BinID = *p.BinID
	}
	if p.Quantity != nil {
		item.Quantity = *p.Quantity
	}
	if p.Moved != nil {
		item.Moved = *p.Moved
	}
	if p.Reason != nil {
		item.Reason = *p.Reason
	}
	if p.Reference != nil {
		item.Reference = *p.Reference
	}
	err := item.Validate()
	return item, err
}

// PurchaseOrder is a purchase order record.
type PurchaseOrder struct {
	ID         int                 `json:"id"`
	SupplierID int                 `json:"supplier_id"`
	Ordered    string              `json:"ordered"`
	Expected   string              `json:"expected"`
	Total      float64             `json:"total"`
	Status     PurchaseOrderStatus `json:"status"`
	Notes      string              `json:"notes"`
}
