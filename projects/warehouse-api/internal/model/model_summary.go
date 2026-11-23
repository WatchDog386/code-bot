package model

import (
	"cmp"
	"fmt"
)

// Summary is one line for logs and lists.
func (s StockCount) Summary() string {
	return fmt.Sprintf("StockCount #%d: %s", s.ID, s.Counter)
}

// Map is the record as plain values (for CSV export and templates).
func (s StockCount) Map() map[string]any {
	return map[string]any{
		"id":         s.ID,
		"bin_id":     s.BinID,
		"product_id": s.ProductID,
		"counted":    s.Counted,
		"expected":   s.Expected,
		"found":      s.Found,
		"counter":    s.Counter,
	}
}

// CompareStockCountByBinID orders stock counts by bin id (for slices.SortFunc).
func CompareStockCountByBinID(a, b StockCount) int {
	return cmp.Compare(a.BinID, b.BinID)
}

// CompareStockCountByProductID orders stock counts by product id (for slices.SortFunc).
func CompareStockCountByProductID(a, b StockCount) int {
	return cmp.Compare(a.ProductID, b.ProductID)
}

// CompareStockCountByCounted orders stock counts by counted (for slices.SortFunc).
func CompareStockCountByCounted(a, b StockCount) int {
	return cmp.Compare(a.Counted, b.Counted)
}

// CompareStockCountByExpected orders stock counts by expected (for slices.SortFunc).
func CompareStockCountByExpected(a, b StockCount) int {
	return cmp.Compare(a.Expected, b.Expected)
}

// CompareStockCountByFound orders stock counts by found (for slices.SortFunc).
func CompareStockCountByFound(a, b StockCount) int {
	return cmp.Compare(a.Found, b.Found)
}
