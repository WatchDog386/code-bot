package model

import (
	"cmp"
	"fmt"
)

// Validate checks every field and normalises text and amounts in place.
func (s *StockMovement) Validate() error {
	var err error
	if err = CheckRef("product_id", s.ProductID); err != nil {
		return err
	}
	if err = CheckRef("bin_id", s.BinID); err != nil {
		return err
	}
	if err = CheckInt("quantity", s.Quantity); err != nil {
		return err
	}
	if err = CheckDate("moved", s.Moved); err != nil {
		return err
	}
	if !s.Reason.Valid() {
		return Invalid("reason", "must be one of %s", StockMovementReasonList())
	}
	if s.Reference, err = CheckText("reference", s.Reference, 120, true); err != nil {
		return err
	}
	return nil
}

// Summary is one line for logs and lists.
func (s StockMovement) Summary() string {
	return fmt.Sprintf("StockMovement #%d: %s", s.ID, s.Reference)
}

// Map is the record as plain values (for CSV export and templates).
func (s StockMovement) Map() map[string]any {
	return map[string]any{
		"id":         s.ID,
		"product_id": s.ProductID,
		"bin_id":     s.BinID,
		"quantity":   s.Quantity,
		"moved":      s.Moved,
		"reason":     string(s.Reason),
		"reference":  s.Reference,
	}
}

// CompareStockMovementByProductID orders stock movements by product id (for slices.SortFunc).
func CompareStockMovementByProductID(a, b StockMovement) int {
	return cmp.Compare(a.ProductID, b.ProductID)
}

// CompareStockMovementByBinID orders stock movements by bin id (for slices.SortFunc).
func CompareStockMovementByBinID(a, b StockMovement) int {
	return cmp.Compare(a.BinID, b.BinID)
}

// CompareStockMovementByQuantity orders stock movements by quantity (for slices.SortFunc).
func CompareStockMovementByQuantity(a, b StockMovement) int {
	return cmp.Compare(a.Quantity, b.Quantity)
}

// CompareStockMovementByMoved orders stock movements by moved (for slices.SortFunc).
func CompareStockMovementByMoved(a, b StockMovement) int {
	return cmp.Compare(a.Moved, b.Moved)
}

// CompareStockMovementByReason orders stock movements by reason (for slices.SortFunc).
func CompareStockMovementByReason(a, b StockMovement) int {
	return cmp.Compare(string(a.Reason), string(b.Reason))
}
