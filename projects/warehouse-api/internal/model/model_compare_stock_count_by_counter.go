package model

import "cmp"

// CompareStockCountByCounter orders stock counts by counter (for slices.SortFunc).
func CompareStockCountByCounter(a, b StockCount) int {
	return cmp.Compare(a.Counter, b.Counter)
}

// StockCountPatch changes some fields of a StockCount; nil means "leave as it is".
type StockCountPatch struct {
	BinID     *int    `json:"bin_id,omitempty"`
	ProductID *int    `json:"product_id,omitempty"`
	Counted   *string `json:"counted,omitempty"`
	Expected  *int    `json:"expected,omitempty"`
	Found     *int    `json:"found,omitempty"`
	Counter   *string `json:"counter,omitempty"`
}

// Apply returns a validated copy of item with the patch applied.
func (p StockCountPatch) Apply(item StockCount) (StockCount, error) {
	if p.BinID != nil {
		item.BinID = *p.BinID
	}
	if p.ProductID != nil {
		item.ProductID = *p.ProductID
	}
	if p.Counted != nil {
		item.Counted = *p.Counted
	}
	if p.Expected != nil {
		item.Expected = *p.Expected
	}
	if p.Found != nil {
		item.Found = *p.Found
	}
	if p.Counter != nil {
		item.Counter = *p.Counter
	}
	err := item.Validate()
	return item, err
}
