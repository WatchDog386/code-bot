package model

import (
	"cmp"
	"fmt"
	"math"
)

// Validate checks every field and normalises text and amounts in place.
func (p *PurchaseOrder) Validate() error {
	var err error
	if err = CheckRef("supplier_id", p.SupplierID); err != nil {
		return err
	}
	if err = CheckDate("ordered", p.Ordered); err != nil {
		return err
	}
	if err = CheckDate("expected", p.Expected); err != nil {
		return err
	}
	if err = CheckNumber("total", p.Total); err != nil {
		return err
	}
	p.Total = math.Round(p.Total*100) / 100
	if !p.Status.Valid() {
		return Invalid("status", "must be one of %s", PurchaseOrderStatusList())
	}
	if p.Notes, err = CheckText("notes", p.Notes, 2000, false); err != nil {
		return err
	}
	return nil
}

// Summary is one line for logs and lists.
func (p PurchaseOrder) Summary() string {
	return fmt.Sprintf("PurchaseOrder #%d", p.ID)
}

// Map is the record as plain values (for CSV export and templates).
func (p PurchaseOrder) Map() map[string]any {
	return map[string]any{
		"id":          p.ID,
		"supplier_id": p.SupplierID,
		"ordered":     p.Ordered,
		"expected":    p.Expected,
		"total":       p.Total,
		"status":      string(p.Status),
		"notes":       p.Notes,
	}
}

// ComparePurchaseOrderBySupplierID orders purchase orders by supplier id (for slices.SortFunc).
func ComparePurchaseOrderBySupplierID(a, b PurchaseOrder) int {
	return cmp.Compare(a.SupplierID, b.SupplierID)
}

// ComparePurchaseOrderByOrdered orders purchase orders by ordered (for slices.SortFunc).
func ComparePurchaseOrderByOrdered(a, b PurchaseOrder) int {
	return cmp.Compare(a.Ordered, b.Ordered)
}

// ComparePurchaseOrderByExpected orders purchase orders by expected (for slices.SortFunc).
func ComparePurchaseOrderByExpected(a, b PurchaseOrder) int {
	return cmp.Compare(a.Expected, b.Expected)
}

// ComparePurchaseOrderByTotal orders purchase orders by total (for slices.SortFunc).
func ComparePurchaseOrderByTotal(a, b PurchaseOrder) int {
	return cmp.Compare(a.Total, b.Total)
}

// ComparePurchaseOrderByStatus orders purchase orders by status (for slices.SortFunc).
func ComparePurchaseOrderByStatus(a, b PurchaseOrder) int {
	return cmp.Compare(string(a.Status), string(b.Status))
}

// ComparePurchaseOrderByNotes orders purchase orders by notes (for slices.SortFunc).
func ComparePurchaseOrderByNotes(a, b PurchaseOrder) int {
	return cmp.Compare(a.Notes, b.Notes)
}

// PurchaseOrderPatch changes some fields of a PurchaseOrder; nil means "leave as it is".
type PurchaseOrderPatch struct {
	SupplierID *int                 `json:"supplier_id,omitempty"`
	Ordered    *string              `json:"ordered,omitempty"`
	Expected   *string              `json:"expected,omitempty"`
	Total      *float64             `json:"total,omitempty"`
	Status     *PurchaseOrderStatus `json:"status,omitempty"`
	Notes      *string              `json:"notes,omitempty"`
}
