// Package service holds the Warehouse Inventory business rules: validation, links between
// records, small domain operations and statistics.
package service

import (
	"errors"
	"fmt"
	"math"

	"warehouse-api/internal/model"
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
	Documents      *store.DocumentStore
	Notifications  *store.NotificationStore
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
		Documents:      store.NewDocumentStore(),
		Notifications:  store.NewNotificationStore(),
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
		if _, err := s.CreateDocument(SampleDocument(i)); err != nil {
			return err
		}
		if _, err := s.CreateNotification(SampleNotification(i)); err != nil {
			return err
		}
	}
	return nil
}

// CreateSupplier validates and stores a new supplier.
func (s *Service) CreateSupplier(item model.Supplier) (model.Supplier, error) {
	item.ID = 0
	if err := item.Validate(); err != nil {
		return model.Supplier{}, err
	}
	if err := s.checkSupplierLinks(item); err != nil {
		return model.Supplier{}, err
	}
	return s.Suppliers.Create(item), nil
}

// GetSupplier returns one supplier.
func (s *Service) GetSupplier(id int) (model.Supplier, error) {
	item, ok := s.Suppliers.Get(id)
	if !ok {
		return model.Supplier{}, notFound("supplier", id)
	}
	return item, nil
}

// ListSuppliers returns every supplier, oldest first.
func (s *Service) ListSuppliers() []model.Supplier {
	return s.Suppliers.List()
}

// UpdateSupplier applies patch to a supplier.
func (s *Service) UpdateSupplier(id int, patch model.SupplierPatch) (model.Supplier, error) {
	current, err := s.GetSupplier(id)
	if err != nil {
		return model.Supplier{}, err
	}
	updated, err := patch.Apply(current)
	if err != nil {
		return model.Supplier{}, err
	}
	if err := s.checkSupplierLinks(updated); err != nil {
		return model.Supplier{}, err
	}
	s.Suppliers.Update(updated)
	return updated, nil
}

// DeleteSupplier removes a supplier nothing points at any more.
func (s *Service) DeleteSupplier(id int) error {
	if _, err := s.GetSupplier(id); err != nil {
		return err
	}
	if n := s.Products.CountForSupplier(id); n > 0 {
		return inUse("supplier", id, n, "products")
	}
	if n := s.PurchaseOrders.CountForSupplier(id); n > 0 {
		return inUse("supplier", id, n, "purchase orders")
	}
	if n := s.Documents.CountForSupplier(id); n > 0 {
		return inUse("supplier", id, n, "documents")
	}
	s.Suppliers.Delete(id)
	return nil
}

// checkSupplierLinks makes sure every record a supplier points at exists.
func (s *Service) checkSupplierLinks(_ model.Supplier) error {
	return nil
}

// AdjustSupplierLeadDays adds delta to the lead days of a supplier (it can't go below zero).
func (s *Service) AdjustSupplierLeadDays(id int, delta int) (model.Supplier, error) {
	item, err := s.GetSupplier(id)
	if err != nil {
		return model.Supplier{}, err
	}
	value := item.LeadDays + delta
	return s.UpdateSupplier(id, model.SupplierPatch{LeadDays: &value})
}

// ToggleSupplierPreferred flips the preferred flag of a supplier.
func (s *Service) ToggleSupplierPreferred(id int) (model.Supplier, error) {
	item, err := s.GetSupplier(id)
	if err != nil {
		return model.Supplier{}, err
	}
	flipped := !item.Preferred
	return s.UpdateSupplier(id, model.SupplierPatch{Preferred: &flipped})
}

// SupplierStats sums up every supplier.
type SupplierStats struct {
	Count           int     `json:"count"`
	TotalLeadDays   int     `json:"total_lead_days"`
	AverageLeadDays float64 `json:"average_lead_days"`
	Preferred       int     `json:"preferred"`
}

// SupplierStats returns totals and breakdowns over every supplier.
func (s *Service) SupplierStats() SupplierStats {
	return SupplierStats{
		Count:           s.Suppliers.Count(),
		TotalLeadDays:   s.Suppliers.TotalLeadDays(),
		AverageLeadDays: s.Suppliers.AverageLeadDays(),
		Preferred:       len(s.Suppliers.WherePreferred(true)),
	}
}

// SampleSupplier returns valid data for a new supplier (links point at seeded records).
func SampleSupplier(i int) model.Supplier {
	return model.Supplier{
		Name:      fmt.Sprintf("Supplier name %d", i),
		Email:     fmt.Sprintf("supplier%d@example.com", i),
		Phone:     fmt.Sprintf("Supplier phone %d", i),
		Country:   fmt.Sprintf("Supplier country %d", i),
		LeadDays:  i + 1,
		Preferred: i%2 == 1,
	}
}

// CreateProduct validates and stores a new product.
func (s *Service) CreateProduct(item model.Product) (model.Product, error) {
	item.ID = 0
	if err := item.Validate(); err != nil {
		return model.Product{}, err
	}
	if err := s.checkProductLinks(item); err != nil {
		return model.Product{}, err
	}
	return s.Products.Create(item), nil
}

// GetProduct returns one product.
func (s *Service) GetProduct(id int) (model.Product, error) {
	item, ok := s.Products.Get(id)
	if !ok {
		return model.Product{}, notFound("product", id)
	}
	return item, nil
}

// ListProducts returns every product, oldest first.
func (s *Service) ListProducts() []model.Product {
	return s.Products.List()
}

// UpdateProduct applies patch to a product.
func (s *Service) UpdateProduct(id int, patch model.ProductPatch) (model.Product, error) {
	current, err := s.GetProduct(id)
	if err != nil {
		return model.Product{}, err
	}
	updated, err := patch.Apply(current)
	if err != nil {
		return model.Product{}, err
	}
	if err := s.checkProductLinks(updated); err != nil {
		return model.Product{}, err
	}
	s.Products.Update(updated)
	return updated, nil
}

// DeleteProduct removes a product nothing points at any more.
func (s *Service) DeleteProduct(id int) error {
	if _, err := s.GetProduct(id); err != nil {
		return err
	}
	if n := s.StockMovements.CountForProduct(id); n > 0 {
		return inUse("product", id, n, "stock movements")
	}
	if n := s.StockCounts.CountForProduct(id); n > 0 {
		return inUse("product", id, n, "stock counts")
	}
	s.Products.Delete(id)
	return nil
}

// checkProductLinks makes sure every record a product points at exists.
func (s *Service) checkProductLinks(item model.Product) error {
	if _, ok := s.Suppliers.Get(item.SupplierID); !ok {
		return notFound("supplier", item.SupplierID)
	}
	return nil
}

// AdjustProductUnitCost adds delta to the unit cost of a product (it can't go below zero).
func (s *Service) AdjustProductUnitCost(id int, delta float64) (model.Product, error) {
	item, err := s.GetProduct(id)
	if err != nil {
		return model.Product{}, err
	}
	value := math.Round((item.UnitCost+delta)*100) / 100
	return s.UpdateProduct(id, model.ProductPatch{UnitCost: &value})
}

// AdjustProductUnitPrice adds delta to the unit price of a product (it can't go below zero).
func (s *Service) AdjustProductUnitPrice(id int, delta float64) (model.Product, error) {
	item, err := s.GetProduct(id)
	if err != nil {
		return model.Product{}, err
	}
	value := math.Round((item.UnitPrice+delta)*100) / 100
	return s.UpdateProduct(id, model.ProductPatch{UnitPrice: &value})
}

// AdjustProductReorderLevel adds delta to the reorder level of a product (it can't go below zero).
func (s *Service) AdjustProductReorderLevel(id int, delta int) (model.Product, error) {
	item, err := s.GetProduct(id)
	if err != nil {
		return model.Product{}, err
	}
	value := item.ReorderLevel + delta
	return s.UpdateProduct(id, model.ProductPatch{ReorderLevel: &value})
}

// SetProductCategory moves a product to another category.
func (s *Service) SetProductCategory(id int, value model.ProductCategory) (model.Product, error) {
	return s.UpdateProduct(id, model.ProductPatch{Category: &value})
}

// ToggleProductActive flips the active flag of a product.
func (s *Service) ToggleProductActive(id int) (model.Product, error) {
	item, err := s.GetProduct(id)
	if err != nil {
		return model.Product{}, err
	}
	flipped := !item.Active
	return s.UpdateProduct(id, model.ProductPatch{Active: &flipped})
}

// ProductStats sums up every product.
type ProductStats struct {
	Count               int                           `json:"count"`
	TotalUnitCost       float64                       `json:"total_unit_cost"`
	AverageUnitCost     float64                       `json:"average_unit_cost"`
	TotalUnitPrice      float64                       `json:"total_unit_price"`
	AverageUnitPrice    float64                       `json:"average_unit_price"`
	TotalReorderLevel   int                           `json:"total_reorder_level"`
	AverageReorderLevel float64                       `json:"average_reorder_level"`
	ByCategory          map[model.ProductCategory]int `json:"by_category"`
	Active              int                           `json:"active"`
}

// ProductStats returns totals and breakdowns over every product.
func (s *Service) ProductStats() ProductStats {
	return ProductStats{
		Count:               s.Products.Count(),
		TotalUnitCost:       s.Products.TotalUnitCost(),
		AverageUnitCost:     s.Products.AverageUnitCost(),
		TotalUnitPrice:      s.Products.TotalUnitPrice(),
		AverageUnitPrice:    s.Products.AverageUnitPrice(),
		TotalReorderLevel:   s.Products.TotalReorderLevel(),
		AverageReorderLevel: s.Products.AverageReorderLevel(),
		ByCategory:          s.Products.CountByCategory(),
		Active:              len(s.Products.WhereActive(true)),
	}
}

// SampleProduct returns valid data for a new product (links point at seeded records).
func SampleProduct(i int) model.Product {
	return model.Product{
		SupplierID:   (i-1)%3 + 1,
		Sku:          fmt.Sprintf("Product sku %d", i),
		Name:         fmt.Sprintf("Product name %d", i),
		UnitCost:     math.Round((10*float64(i)+0.99)*100) / 100,
		UnitPrice:    math.Round((10*float64(i)+0.99)*100) / 100,
		ReorderLevel: i + 1,
		Category:     model.ProductCategoryValues[i%5],
		Active:       i%2 == 1,
	}
}

// CreateBin validates and stores a new bin.
func (s *Service) CreateBin(item model.Bin) (model.Bin, error) {
	item.ID = 0
	if err := item.Validate(); err != nil {
		return model.Bin{}, err
	}
	if err := s.checkBinLinks(item); err != nil {
		return model.Bin{}, err
	}
	return s.Bins.Create(item), nil
}

// GetBin returns one bin.
func (s *Service) GetBin(id int) (model.Bin, error) {
	item, ok := s.Bins.Get(id)
	if !ok {
		return model.Bin{}, notFound("bin", id)
	}
	return item, nil
}

// ListBins returns every bin, oldest first.
func (s *Service) ListBins() []model.Bin {
	return s.Bins.List()
}

// UpdateBin applies patch to a bin.
func (s *Service) UpdateBin(id int, patch model.BinPatch) (model.Bin, error) {
	current, err := s.GetBin(id)
	if err != nil {
		return model.Bin{}, err
	}
	updated, err := patch.Apply(current)
	if err != nil {
		return model.Bin{}, err
	}
	if err := s.checkBinLinks(updated); err != nil {
		return model.Bin{}, err
	}
	s.Bins.Update(updated)
	return updated, nil
}

// DeleteBin removes a bin nothing points at any more.
func (s *Service) DeleteBin(id int) error {
	if _, err := s.GetBin(id); err != nil {
		return err
	}
	if n := s.StockMovements.CountForBin(id); n > 0 {
		return inUse("bin", id, n, "stock movements")
	}
	if n := s.StockCounts.CountForBin(id); n > 0 {
		return inUse("bin", id, n, "stock counts")
	}
	s.Bins.Delete(id)
	return nil
}

// checkBinLinks makes sure every record a bin points at exists.
func (s *Service) checkBinLinks(_ model.Bin) error {
	return nil
}

// AdjustBinShelf adds delta to the shelf of a bin (it can't go below zero).
func (s *Service) AdjustBinShelf(id int, delta int) (model.Bin, error) {
	item, err := s.GetBin(id)
	if err != nil {
		return model.Bin{}, err
	}
	value := item.Shelf + delta
	return s.UpdateBin(id, model.BinPatch{Shelf: &value})
}

// AdjustBinCapacity adds delta to the capacity of a bin (it can't go below zero).
func (s *Service) AdjustBinCapacity(id int, delta int) (model.Bin, error) {
	item, err := s.GetBin(id)
	if err != nil {
		return model.Bin{}, err
	}
	value := item.Capacity + delta
	return s.UpdateBin(id, model.BinPatch{Capacity: &value})
}

// ToggleBinRefrigerated flips the refrigerated flag of a bin.
func (s *Service) ToggleBinRefrigerated(id int) (model.Bin, error) {
	item, err := s.GetBin(id)
	if err != nil {
		return model.Bin{}, err
	}
	flipped := !item.Refrigerated
	return s.UpdateBin(id, model.BinPatch{Refrigerated: &flipped})
}

// BinStats sums up every bin.
type BinStats struct {
	Count           int     `json:"count"`
	TotalShelf      int     `json:"total_shelf"`
	AverageShelf    float64 `json:"average_shelf"`
	TotalCapacity   int     `json:"total_capacity"`
	AverageCapacity float64 `json:"average_capacity"`
	Refrigerated    int     `json:"refrigerated"`
}

// BinStats returns totals and breakdowns over every bin.
func (s *Service) BinStats() BinStats {
	return BinStats{
		Count:           s.Bins.Count(),
		TotalShelf:      s.Bins.TotalShelf(),
		AverageShelf:    s.Bins.AverageShelf(),
		TotalCapacity:   s.Bins.TotalCapacity(),
		AverageCapacity: s.Bins.AverageCapacity(),
		Refrigerated:    len(s.Bins.WhereRefrigerated(true)),
	}
}

// SampleBin returns valid data for a new bin (links point at seeded records).
func SampleBin(i int) model.Bin {
	return model.Bin{
		Code:         fmt.Sprintf("Bin code %d", i),
		Aisle:        fmt.Sprintf("Bin aisle %d", i),
		Shelf:        i + 1,
		Capacity:     i + 1,
		Refrigerated: i%2 == 1,
	}
}

// CreateStockMovement validates and stores a new stock movement.
func (s *Service) CreateStockMovement(item model.StockMovement) (model.StockMovement, error) {
	item.ID = 0
	if err := item.Validate(); err != nil {
		return model.StockMovement{}, err
	}
	if err := s.checkStockMovementLinks(item); err != nil {
		return model.StockMovement{}, err
	}
	return s.StockMovements.Create(item), nil
}

// GetStockMovement returns one stock movement.
func (s *Service) GetStockMovement(id int) (model.StockMovement, error) {
	item, ok := s.StockMovements.Get(id)
	if !ok {
		return model.StockMovement{}, notFound("stock movement", id)
	}
	return item, nil
}

// ListStockMovements returns every stock movement, oldest first.
func (s *Service) ListStockMovements() []model.StockMovement {
	return s.StockMovements.List()
}

// UpdateStockMovement applies patch to a stock movement.
func (s *Service) UpdateStockMovement(id int, patch model.StockMovementPatch) (model.StockMovement, error) {
	current, err := s.GetStockMovement(id)
	if err != nil {
		return model.StockMovement{}, err
	}
	updated, err := patch.Apply(current)
	if err != nil {
		return model.StockMovement{}, err
	}
	if err := s.checkStockMovementLinks(updated); err != nil {
		return model.StockMovement{}, err
	}
	s.StockMovements.Update(updated)
	return updated, nil
}

// DeleteStockMovement removes a stock movement nothing points at any more.
func (s *Service) DeleteStockMovement(id int) error {
	if _, err := s.GetStockMovement(id); err != nil {
		return err
	}
	s.StockMovements.Delete(id)
	return nil
}

// checkStockMovementLinks makes sure every record a stock movement points at exists.
func (s *Service) checkStockMovementLinks(item model.StockMovement) error {
	if _, ok := s.Products.Get(item.ProductID); !ok {
		return notFound("product", item.ProductID)
	}
	if _, ok := s.Bins.Get(item.BinID); !ok {
		return notFound("bin", item.BinID)
	}
	return nil
}

// AdjustStockMovementQuantity adds delta to the quantity of a stock movement (it can't go below zero).
func (s *Service) AdjustStockMovementQuantity(id int, delta int) (model.StockMovement, error) {
	item, err := s.GetStockMovement(id)
	if err != nil {
		return model.StockMovement{}, err
	}
	value := item.Quantity + delta
	return s.UpdateStockMovement(id, model.StockMovementPatch{Quantity: &value})
}

// SetStockMovementReason moves a stock movement to another reason.
func (s *Service) SetStockMovementReason(id int, value model.StockMovementReason) (model.StockMovement, error) {
	return s.UpdateStockMovement(id, model.StockMovementPatch{Reason: &value})
}

// StockMovementStats sums up every stock movement.
type StockMovementStats struct {
	Count           int                               `json:"count"`
	TotalQuantity   int                               `json:"total_quantity"`
	AverageQuantity float64                           `json:"average_quantity"`
	ByReason        map[model.StockMovementReason]int `json:"by_reason"`
}

// StockMovementStats returns totals and breakdowns over every stock movement.
func (s *Service) StockMovementStats() StockMovementStats {
	return StockMovementStats{
		Count:           s.StockMovements.Count(),
		TotalQuantity:   s.StockMovements.TotalQuantity(),
		AverageQuantity: s.StockMovements.AverageQuantity(),
		ByReason:        s.StockMovements.CountByReason(),
	}
}

// SampleStockMovement returns valid data for a new stock movement (links point at seeded records).
func SampleStockMovement(i int) model.StockMovement {
	return model.StockMovement{
		ProductID: (i-1)%3 + 1,
		BinID:     (i-1)%3 + 1,
		Quantity:  i + 1,
		Moved:     fmt.Sprintf("2026-%02d-%02d", i%12+1, i%28+1),
		Reason:    model.StockMovementReasonValues[i%5],
		Reference: fmt.Sprintf("Stock movement reference %d", i),
	}
}

// CreatePurchaseOrder validates and stores a new purchase order.
func (s *Service) CreatePurchaseOrder(item model.PurchaseOrder) (model.PurchaseOrder, error) {
	item.ID = 0
	if err := item.Validate(); err != nil {
		return model.PurchaseOrder{}, err
	}
	if err := s.checkPurchaseOrderLinks(item); err != nil {
		return model.PurchaseOrder{}, err
	}
	return s.PurchaseOrders.Create(item), nil
}

// GetPurchaseOrder returns one purchase order.
func (s *Service) GetPurchaseOrder(id int) (model.PurchaseOrder, error) {
	item, ok := s.PurchaseOrders.Get(id)
	if !ok {
		return model.PurchaseOrder{}, notFound("purchase order", id)
	}
	return item, nil
}

// ListPurchaseOrders returns every purchase order, oldest first.
func (s *Service) ListPurchaseOrders() []model.PurchaseOrder {
	return s.PurchaseOrders.List()
}

// UpdatePurchaseOrder applies patch to a purchase order.
func (s *Service) UpdatePurchaseOrder(id int, patch model.PurchaseOrderPatch) (model.PurchaseOrder, error) {
	current, err := s.GetPurchaseOrder(id)
	if err != nil {
		return model.PurchaseOrder{}, err
	}
	updated, err := patch.Apply(current)
	if err != nil {
		return model.PurchaseOrder{}, err
	}
	if err := s.checkPurchaseOrderLinks(updated); err != nil {
		return model.PurchaseOrder{}, err
	}
	s.PurchaseOrders.Update(updated)
	return updated, nil
}

// DeletePurchaseOrder removes a purchase order nothing points at any more.
func (s *Service) DeletePurchaseOrder(id int) error {
	if _, err := s.GetPurchaseOrder(id); err != nil {
		return err
	}
	s.PurchaseOrders.Delete(id)
	return nil
}

// checkPurchaseOrderLinks makes sure every record a purchase order points at exists.
func (s *Service) checkPurchaseOrderLinks(item model.PurchaseOrder) error {
	if _, ok := s.Suppliers.Get(item.SupplierID); !ok {
		return notFound("supplier", item.SupplierID)
	}
	return nil
}

// AdjustPurchaseOrderTotal adds delta to the total of a purchase order (it can't go below zero).
func (s *Service) AdjustPurchaseOrderTotal(id int, delta float64) (model.PurchaseOrder, error) {
	item, err := s.GetPurchaseOrder(id)
	if err != nil {
		return model.PurchaseOrder{}, err
	}
	value := math.Round((item.Total+delta)*100) / 100
	return s.UpdatePurchaseOrder(id, model.PurchaseOrderPatch{Total: &value})
}

// SetPurchaseOrderStatus moves a purchase order to another status.
func (s *Service) SetPurchaseOrderStatus(id int, value model.PurchaseOrderStatus) (model.PurchaseOrder, error) {
	return s.UpdatePurchaseOrder(id, model.PurchaseOrderPatch{Status: &value})
}

// PurchaseOrderStats sums up every purchase order.
type PurchaseOrderStats struct {
	Count        int                               `json:"count"`
	TotalTotal   float64                           `json:"total_total"`
	AverageTotal float64                           `json:"average_total"`
	ByStatus     map[model.PurchaseOrderStatus]int `json:"by_status"`
}

// PurchaseOrderStats returns totals and breakdowns over every purchase order.
func (s *Service) PurchaseOrderStats() PurchaseOrderStats {
	return PurchaseOrderStats{
		Count:        s.PurchaseOrders.Count(),
		TotalTotal:   s.PurchaseOrders.TotalTotal(),
		AverageTotal: s.PurchaseOrders.AverageTotal(),
		ByStatus:     s.PurchaseOrders.CountByStatus(),
	}
}

// SamplePurchaseOrder returns valid data for a new purchase order (links point at seeded records).
func SamplePurchaseOrder(i int) model.PurchaseOrder {
	return model.PurchaseOrder{
		SupplierID: (i-1)%3 + 1,
		Ordered:    fmt.Sprintf("2026-%02d-%02d", i%12+1, i%28+1),
		Expected:   fmt.Sprintf("2026-%02d-%02d", i%12+1, i%28+1),
		Total:      math.Round((10*float64(i)+0.99)*100) / 100,
		Status:     model.PurchaseOrderStatusValues[i%5],
		Notes:      fmt.Sprintf("Notes about purchase order %d.", i),
	}
}

// CreateStockCount validates and stores a new stock count.
func (s *Service) CreateStockCount(item model.StockCount) (model.StockCount, error) {
	item.ID = 0
	if err := item.Validate(); err != nil {
		return model.StockCount{}, err
	}
	if err := s.checkStockCountLinks(item); err != nil {
		return model.StockCount{}, err
	}
	return s.StockCounts.Create(item), nil
}

// GetStockCount returns one stock count.
func (s *Service) GetStockCount(id int) (model.StockCount, error) {
	item, ok := s.StockCounts.Get(id)
	if !ok {
		return model.StockCount{}, notFound("stock count", id)
	}
	return item, nil
}

// ListStockCounts returns every stock count, oldest first.
func (s *Service) ListStockCounts() []model.StockCount {
	return s.StockCounts.List()
}

// UpdateStockCount applies patch to a stock count.
func (s *Service) UpdateStockCount(id int, patch model.StockCountPatch) (model.StockCount, error) {
	current, err := s.GetStockCount(id)
	if err != nil {
		return model.StockCount{}, err
	}
	updated, err := patch.Apply(current)
	if err != nil {
		return model.StockCount{}, err
	}
	if err := s.checkStockCountLinks(updated); err != nil {
		return model.StockCount{}, err
	}
	s.StockCounts.Update(updated)
	return updated, nil
}

// DeleteStockCount removes a stock count nothing points at any more.
func (s *Service) DeleteStockCount(id int) error {
	if _, err := s.GetStockCount(id); err != nil {
		return err
	}
	s.StockCounts.Delete(id)
	return nil
}

// checkStockCountLinks makes sure every record a stock count points at exists.
func (s *Service) checkStockCountLinks(item model.StockCount) error {
	if _, ok := s.Bins.Get(item.BinID); !ok {
		return notFound("bin", item.BinID)
	}
	if _, ok := s.Products.Get(item.ProductID); !ok {
		return notFound("product", item.ProductID)
	}
	return nil
}

// AdjustStockCountExpected adds delta to the expected of a stock count (it can't go below zero).
func (s *Service) AdjustStockCountExpected(id int, delta int) (model.StockCount, error) {
	item, err := s.GetStockCount(id)
	if err != nil {
		return model.StockCount{}, err
	}
	value := item.Expected + delta
	return s.UpdateStockCount(id, model.StockCountPatch{Expected: &value})
}

// AdjustStockCountFound adds delta to the found of a stock count (it can't go below zero).
func (s *Service) AdjustStockCountFound(id int, delta int) (model.StockCount, error) {
	item, err := s.GetStockCount(id)
	if err != nil {
		return model.StockCount{}, err
	}
	value := item.Found + delta
	return s.UpdateStockCount(id, model.StockCountPatch{Found: &value})
}

// StockCountStats sums up every stock count.
type StockCountStats struct {
	Count           int     `json:"count"`
	TotalExpected   int     `json:"total_expected"`
	AverageExpected float64 `json:"average_expected"`
	TotalFound      int     `json:"total_found"`
	AverageFound    float64 `json:"average_found"`
}

// StockCountStats returns totals and breakdowns over every stock count.
func (s *Service) StockCountStats() StockCountStats {
	return StockCountStats{
		Count:           s.StockCounts.Count(),
		TotalExpected:   s.StockCounts.TotalExpected(),
		AverageExpected: s.StockCounts.AverageExpected(),
		TotalFound:      s.StockCounts.TotalFound(),
		AverageFound:    s.StockCounts.AverageFound(),
	}
}

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

// CreateDocument validates and stores a new document.
func (s *Service) CreateDocument(item model.Document) (model.Document, error) {
	item.ID = 0
	if err := item.Validate(); err != nil {
		return model.Document{}, err
	}
	if err := s.checkDocumentLinks(item); err != nil {
		return model.Document{}, err
	}
	return s.Documents.Create(item), nil
}

// GetDocument returns one document.
func (s *Service) GetDocument(id int) (model.Document, error) {
	item, ok := s.Documents.Get(id)
	if !ok {
		return model.Document{}, notFound("document", id)
	}
	return item, nil
}

// ListDocuments returns every document, oldest first.
func (s *Service) ListDocuments() []model.Document {
	return s.Documents.List()
}

// UpdateDocument applies patch to a document.
func (s *Service) UpdateDocument(id int, patch model.DocumentPatch) (model.Document, error) {
	current, err := s.GetDocument(id)
	if err != nil {
		return model.Document{}, err
	}
	updated, err := patch.Apply(current)
	if err != nil {
		return model.Document{}, err
	}
	if err := s.checkDocumentLinks(updated); err != nil {
		return model.Document{}, err
	}
	s.Documents.Update(updated)
	return updated, nil
}

// DeleteDocument removes a document nothing points at any more.
func (s *Service) DeleteDocument(id int) error {
	if _, err := s.GetDocument(id); err != nil {
		return err
	}
	s.Documents.Delete(id)
	return nil
}

// checkDocumentLinks makes sure every record a document points at exists.
func (s *Service) checkDocumentLinks(item model.Document) error {
	if _, ok := s.Suppliers.Get(item.SupplierID); !ok {
		return notFound("supplier", item.SupplierID)
	}
	return nil
}

// AdjustDocumentPages adds delta to the pages of a document (it can't go below zero).
func (s *Service) AdjustDocumentPages(id int, delta int) (model.Document, error) {
	item, err := s.GetDocument(id)
	if err != nil {
		return model.Document{}, err
	}
	value := item.Pages + delta
	return s.UpdateDocument(id, model.DocumentPatch{Pages: &value})
}

// ToggleDocumentSigned flips the signed flag of a document.
func (s *Service) ToggleDocumentSigned(id int) (model.Document, error) {
	item, err := s.GetDocument(id)
	if err != nil {
		return model.Document{}, err
	}
	flipped := !item.Signed
	return s.UpdateDocument(id, model.DocumentPatch{Signed: &flipped})
}

// AdjustDocumentVersion adds delta to the version of a document (it can't go below zero).
func (s *Service) AdjustDocumentVersion(id int, delta int) (model.Document, error) {
	item, err := s.GetDocument(id)
	if err != nil {
		return model.Document{}, err
	}
	value := item.Version + delta
	return s.UpdateDocument(id, model.DocumentPatch{Version: &value})
}

// DocumentStats sums up every document.
type DocumentStats struct {
	Count          int     `json:"count"`
	TotalPages     int     `json:"total_pages"`
	AveragePages   float64 `json:"average_pages"`
	Signed         int     `json:"signed"`
	TotalVersion   int     `json:"total_version"`
	AverageVersion float64 `json:"average_version"`
}

// DocumentStats returns totals and breakdowns over every document.
func (s *Service) DocumentStats() DocumentStats {
	return DocumentStats{
		Count:          s.Documents.Count(),
		TotalPages:     s.Documents.TotalPages(),
		AveragePages:   s.Documents.AveragePages(),
		Signed:         len(s.Documents.WhereSigned(true)),
		TotalVersion:   s.Documents.TotalVersion(),
		AverageVersion: s.Documents.AverageVersion(),
	}
}

// SampleDocument returns valid data for a new document (links point at seeded records).
func SampleDocument(i int) model.Document {
	return model.Document{
		SupplierID: (i-1)%3 + 1,
		Title:      fmt.Sprintf("Document title %d", i),
		Pages:      i + 1,
		Signed:     i%2 == 1,
		Version:    i + 1,
		Issued:     fmt.Sprintf("2026-%02d-%02d", i%12+1, i%28+1),
	}
}

// CreateNotification validates and stores a new notification.
func (s *Service) CreateNotification(item model.Notification) (model.Notification, error) {
	item.ID = 0
	if err := item.Validate(); err != nil {
		return model.Notification{}, err
	}
	if err := s.checkNotificationLinks(item); err != nil {
		return model.Notification{}, err
	}
	return s.Notifications.Create(item), nil
}

// GetNotification returns one notification.
func (s *Service) GetNotification(id int) (model.Notification, error) {
	item, ok := s.Notifications.Get(id)
	if !ok {
		return model.Notification{}, notFound("notification", id)
	}
	return item, nil
}

// ListNotifications returns every notification, oldest first.
func (s *Service) ListNotifications() []model.Notification {
	return s.Notifications.List()
}

// UpdateNotification applies patch to a notification.
func (s *Service) UpdateNotification(id int, patch model.NotificationPatch) (model.Notification, error) {
	current, err := s.GetNotification(id)
	if err != nil {
		return model.Notification{}, err
	}
	updated, err := patch.Apply(current)
	if err != nil {
		return model.Notification{}, err
	}
	if err := s.checkNotificationLinks(updated); err != nil {
		return model.Notification{}, err
	}
	s.Notifications.Update(updated)
	return updated, nil
}

// DeleteNotification removes a notification nothing points at any more.
func (s *Service) DeleteNotification(id int) error {
	if _, err := s.GetNotification(id); err != nil {
		return err
	}
	s.Notifications.Delete(id)
	return nil
}

// checkNotificationLinks makes sure every record a notification points at exists.
func (s *Service) checkNotificationLinks(_ model.Notification) error {
	return nil
}

// SetNotificationChannel moves a notification to another channel.
func (s *Service) SetNotificationChannel(id int, value model.NotificationChannel) (model.Notification, error) {
	return s.UpdateNotification(id, model.NotificationPatch{Channel: &value})
}

// ToggleNotificationRead flips the read flag of a notification.
func (s *Service) ToggleNotificationRead(id int) (model.Notification, error) {
	item, err := s.GetNotification(id)
	if err != nil {
		return model.Notification{}, err
	}
	flipped := !item.Read
	return s.UpdateNotification(id, model.NotificationPatch{Read: &flipped})
}

// NotificationStats sums up every notification.
type NotificationStats struct {
	Count     int                               `json:"count"`
	ByChannel map[model.NotificationChannel]int `json:"by_channel"`
	Read      int                               `json:"read"`
}

// NotificationStats returns totals and breakdowns over every notification.
func (s *Service) NotificationStats() NotificationStats {
	return NotificationStats{
		Count:     s.Notifications.Count(),
		ByChannel: s.Notifications.CountByChannel(),
		Read:      len(s.Notifications.WhereRead(true)),
	}
}

// SampleNotification returns valid data for a new notification (links point at seeded records).
func SampleNotification(i int) model.Notification {
	return model.Notification{
		Recipient: fmt.Sprintf("notification%d@example.com", i),
		Title:     fmt.Sprintf("Notification title %d", i),
		Sent:      fmt.Sprintf("2026-%02d-%02d", i%12+1, i%28+1),
		Channel:   model.NotificationChannelValues[i%3],
		Read:      i%2 == 1,
	}
}
