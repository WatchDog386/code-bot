// Package service holds the Warehouse Inventory business rules: validation, links between
// records, small domain operations and statistics.
package service

import (
	"errors"
	"fmt"

	"warehouse-api/internal/store"
)

// Errors the service returns (wrapped with details).
var (
	ErrNotFound = errors.New("not found")
	ErrConflict = errors.New("conflict")
)

func notFound(entity string, id int) error {
	return fmt.Errorf("%s %d: %w", entity, id, ErrNotFound)
}

func inUse(entity string, id, n int, by string) error {
	return fmt.Errorf("%s %d is still used by %d %s: %w", entity, id, n, by, ErrConflict)
}

// Service is the whole application: every store plus the rules between them.
type Service struct {
	Suppliers      *store.SupplierStore
	Products       *store.ProductStore
	Bins           *store.BinStore
	StockMovements *store.StockMovementStore
	PurchaseOrders *store.PurchaseOrderStore
	StockCounts    *store.StockCountStore
}

// New returns a service with empty stores.
func New() *Service {
	return &Service{
		Suppliers:      store.NewSupplierStore(),
		Products:       store.NewProductStore(),
		Bins:           store.NewBinStore(),
		StockMovements: store.NewStockMovementStore(),
		PurchaseOrders: store.NewPurchaseOrderStore(),
		StockCounts:    store.NewStockCountStore(),
	}
}

// Seed creates n sample records of every kind.
func (s *Service) Seed(n int) error {
	for i := 1; i <= n; i++ {
		if _, err := s.CreateSupplier(SampleSupplier(i)); err != nil {
			return err
		}
		if _, err := s.CreateProduct(SampleProduct(i)); err != nil {
			return err
		}
		if _, err := s.CreateBin(SampleBin(i)); err != nil {
			return err
		}
		if _, err := s.CreateStockMovement(SampleStockMovement(i)); err != nil {
			return err
		}
		if _, err := s.CreatePurchaseOrder(SamplePurchaseOrder(i)); err != nil {
			return err
		}
		if _, err := s.CreateStockCount(SampleStockCount(i)); err != nil {
			return err
		}
	}
	return nil
}
