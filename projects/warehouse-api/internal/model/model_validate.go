package model

import (
	"fmt"
	"math"
)

// Validate checks every field and normalises text and amounts in place.
func (p *Product) Validate() error {
	var err error
	if err = CheckRef("supplier_id", p.SupplierID); err != nil {
		return err
	}
	if p.Sku, err = CheckText("sku", p.Sku, 120, true); err != nil {
		return err
	}
	if p.Name, err = CheckText("name", p.Name, 120, true); err != nil {
		return err
	}
	if err = CheckNumber("unit_cost", p.UnitCost); err != nil {
		return err
	}
	p.UnitCost = math.Round(p.UnitCost*100) / 100
	if err = CheckNumber("unit_price", p.UnitPrice); err != nil {
		return err
	}
	p.UnitPrice = math.Round(p.UnitPrice*100) / 100
	if err = CheckInt("reorder_level", p.ReorderLevel); err != nil {
		return err
	}
	if !p.Category.Valid() {
		return Invalid("category", "must be one of %s", ProductCategoryList())
	}
	return nil
}

// Summary is one line for logs and lists.
func (p Product) Summary() string {
	return fmt.Sprintf("Product #%d: %s", p.ID, p.Sku)
}
