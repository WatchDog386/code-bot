package service

import (
	"fmt"

	"warehouse-api/internal/model"
)

// SampleStockCount returns valid data for a new stock count (links point at seeded records).
func SampleStockCount(i int) model.StockCount {
	return model.StockCount{
		BinID:     (i-1)%3 + 1,
		ProductID: (i-1)%3 + 1,
		Counted:   fmt.Sprintf("2026-%02d-%02d", i%12+1, i%28+1),
		Expected:  i + 1,
		Found:     i + 1,
		Counter:   fmt.Sprintf("Stock count counter %d", i),
	}
}
