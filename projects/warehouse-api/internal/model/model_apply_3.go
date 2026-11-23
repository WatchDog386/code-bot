package model

// Apply returns a validated copy of item with the patch applied.
func (p PurchaseOrderPatch) Apply(item PurchaseOrder) (PurchaseOrder, error) {
	if p.SupplierID != nil {
		item.SupplierID = *p.SupplierID
	}
	if p.Ordered != nil {
		item.Ordered = *p.Ordered
	}
	if p.Expected != nil {
		item.Expected = *p.Expected
	}
	if p.Total != nil {
		item.Total = *p.Total
	}
	if p.Status != nil {
		item.Status = *p.Status
	}
	if p.Notes != nil {
		item.Notes = *p.Notes
	}
	err := item.Validate()
	return item, err
}

// StockCount is a stock count record.
type StockCount struct {
	ID        int    `json:"id"`
	BinID     int    `json:"bin_id"`
	ProductID int    `json:"product_id"`
	Counted   string `json:"counted"`
	Expected  int    `json:"expected"`
	Found     int    `json:"found"`
	Counter   string `json:"counter"`
}

// Validate checks every field and normalises text and amounts in place.
func (s *StockCount) Validate() error {
	var err error
	if err = CheckRef("bin_id", s.BinID); err != nil {
		return err
	}
	if err = CheckRef("product_id", s.ProductID); err != nil {
		return err
	}
	if err = CheckDate("counted", s.Counted); err != nil {
		return err
	}
	if err = CheckInt("expected", s.Expected); err != nil {
		return err
	}
	if err = CheckInt("found", s.Found); err != nil {
		return err
	}
	if s.Counter, err = CheckText("counter", s.Counter, 120, true); err != nil {
		return err
	}
	return nil
}
