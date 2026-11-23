package model

import "fmt"

// Apply returns a validated copy of item with the patch applied.
func (p ProductPatch) Apply(item Product) (Product, error) {
	if p.SupplierID != nil {
		item.SupplierID = *p.SupplierID
	}
	if p.Sku != nil {
		item.Sku = *p.Sku
	}
	if p.Name != nil {
		item.Name = *p.Name
	}
	if p.UnitCost != nil {
		item.UnitCost = *p.UnitCost
	}
	if p.UnitPrice != nil {
		item.UnitPrice = *p.UnitPrice
	}
	if p.ReorderLevel != nil {
		item.ReorderLevel = *p.ReorderLevel
	}
	if p.Category != nil {
		item.Category = *p.Category
	}
	if p.Active != nil {
		item.Active = *p.Active
	}
	err := item.Validate()
	return item, err
}

// Bin is a bin record.
type Bin struct {
	ID           int    `json:"id"`
	Code         string `json:"code"`
	Aisle        string `json:"aisle"`
	Shelf        int    `json:"shelf"`
	Capacity     int    `json:"capacity"`
	Refrigerated bool   `json:"refrigerated"`
}

// Validate checks every field and normalises text and amounts in place.
func (b *Bin) Validate() error {
	var err error
	if b.Code, err = CheckText("code", b.Code, 120, true); err != nil {
		return err
	}
	if b.Aisle, err = CheckText("aisle", b.Aisle, 120, true); err != nil {
		return err
	}
	if err = CheckInt("shelf", b.Shelf); err != nil {
		return err
	}
	if err = CheckInt("capacity", b.Capacity); err != nil {
		return err
	}
	return nil
}

// Summary is one line for logs and lists.
func (b Bin) Summary() string {
	return fmt.Sprintf("Bin #%d: %s", b.ID, b.Code)
}
