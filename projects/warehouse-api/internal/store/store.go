// Package store keeps the Warehouse Inventory records in memory, safe for concurrent use.
package store

import (
	"sort"
	"strings"
	"sync"

	"warehouse-api/internal/model"
)

// SupplierStore keeps every supplier.
type SupplierStore struct {
	mu     sync.RWMutex
	items  map[int]model.Supplier
	nextID int
}

// NewSupplierStore returns an empty store.
func NewSupplierStore() *SupplierStore {
	return &SupplierStore{items: map[int]model.Supplier{}, nextID: 1}
}

// Create stores item under the next id and returns it.
func (s *SupplierStore) Create(item model.Supplier) model.Supplier {
	s.mu.Lock()
	defer s.mu.Unlock()
	item.ID = s.nextID
	s.nextID++
	s.items[item.ID] = item
	return item
}

// Get returns the record with that id.
func (s *SupplierStore) Get(id int) (model.Supplier, bool) {
	s.mu.RLock()
	defer s.mu.RUnlock()
	item, ok := s.items[id]
	return item, ok
}

// List returns every record, oldest first.
func (s *SupplierStore) List() []model.Supplier {
	s.mu.RLock()
	defer s.mu.RUnlock()
	out := make([]model.Supplier, 0, len(s.items))
	for _, item := range s.items {
		out = append(out, item)
	}
	sort.Slice(out, func(i, j int) bool { return out[i].ID < out[j].ID })
	return out
}

// Update replaces an existing record; false if there is none.
func (s *SupplierStore) Update(item model.Supplier) bool {
	s.mu.Lock()
	defer s.mu.Unlock()
	if _, ok := s.items[item.ID]; !ok {
		return false
	}
	s.items[item.ID] = item
	return true
}

// Delete removes a record; false if there was none.
func (s *SupplierStore) Delete(id int) bool {
	s.mu.Lock()
	defer s.mu.Unlock()
	if _, ok := s.items[id]; !ok {
		return false
	}
	delete(s.items, id)
	return true
}

// Count is the number of records.
func (s *SupplierStore) Count() int {
	s.mu.RLock()
	defer s.mu.RUnlock()
	return len(s.items)
}

// Filter returns the records keep() accepts, oldest first.
func (s *SupplierStore) Filter(keep func(model.Supplier) bool) []model.Supplier {
	out := []model.Supplier{}
	for _, item := range s.List() {
		if keep(item) {
			out = append(out, item)
		}
	}
	return out
}

// FindByName returns records whose name is exactly value.
func (s *SupplierStore) FindByName(value string) []model.Supplier {
	return s.Filter(func(item model.Supplier) bool { return item.Name == value })
}

// SearchName returns records whose name contains text (any case).
func (s *SupplierStore) SearchName(text string) []model.Supplier {
	needle := strings.ToLower(strings.TrimSpace(text))
	return s.Filter(func(item model.Supplier) bool { return strings.Contains(strings.ToLower(item.Name), needle) })
}

// FindByEmail returns records whose email is exactly value.
func (s *SupplierStore) FindByEmail(value string) []model.Supplier {
	return s.Filter(func(item model.Supplier) bool { return item.Email == value })
}

// SearchEmail returns records whose email contains text (any case).
func (s *SupplierStore) SearchEmail(text string) []model.Supplier {
	needle := strings.ToLower(strings.TrimSpace(text))
	return s.Filter(func(item model.Supplier) bool { return strings.Contains(strings.ToLower(item.Email), needle) })
}

// FindByPhone returns records whose phone is exactly value.
func (s *SupplierStore) FindByPhone(value string) []model.Supplier {
	return s.Filter(func(item model.Supplier) bool { return item.Phone == value })
}

// SearchPhone returns records whose phone contains text (any case).
func (s *SupplierStore) SearchPhone(text string) []model.Supplier {
	needle := strings.ToLower(strings.TrimSpace(text))
	return s.Filter(func(item model.Supplier) bool { return strings.Contains(strings.ToLower(item.Phone), needle) })
}

// FindByCountry returns records whose country is exactly value.
func (s *SupplierStore) FindByCountry(value string) []model.Supplier {
	return s.Filter(func(item model.Supplier) bool { return item.Country == value })
}

// SearchCountry returns records whose country contains text (any case).
func (s *SupplierStore) SearchCountry(text string) []model.Supplier {
	needle := strings.ToLower(strings.TrimSpace(text))
	return s.Filter(func(item model.Supplier) bool { return strings.Contains(strings.ToLower(item.Country), needle) })
}

// BetweenLeadDays returns records whose lead days is within [low, high].
func (s *SupplierStore) BetweenLeadDays(low, high int) []model.Supplier {
	return s.Filter(func(item model.Supplier) bool { return item.LeadDays >= low && item.LeadDays <= high })
}

// TotalLeadDays adds up the lead days of every record.
func (s *SupplierStore) TotalLeadDays() int {
	var total int
	for _, item := range s.List() {
		total += item.LeadDays
	}
	return total
}

// AverageLeadDays is the mean lead days (0 when there are no records).
func (s *SupplierStore) AverageLeadDays() float64 {
	items := s.List()
	if len(items) == 0 {
		return 0
	}
	return float64(s.TotalLeadDays()) / float64(len(items))
}

// MaxLeadDays returns the record with the highest lead days.
func (s *SupplierStore) MaxLeadDays() (model.Supplier, bool) {
	var best model.Supplier
	found := false
	for _, item := range s.List() {
		if !found || item.LeadDays > best.LeadDays {
			best, found = item, true
		}
	}
	return best, found
}

// WherePreferred returns records whose preferred flag equals flag.
func (s *SupplierStore) WherePreferred(flag bool) []model.Supplier {
	return s.Filter(func(item model.Supplier) bool { return item.Preferred == flag })
}

// Search returns records where any text field contains text (any case).
func (s *SupplierStore) Search(text string) []model.Supplier {
	needle := strings.ToLower(strings.TrimSpace(text))
	return s.Filter(func(item model.Supplier) bool {
		for _, value := range []string{item.Name, item.Email, item.Phone, item.Country} {
			if strings.Contains(strings.ToLower(value), needle) {
				return true
			}
		}
		return false
	})
}

// ProductStore keeps every product.
type ProductStore struct {
	mu     sync.RWMutex
	items  map[int]model.Product
	nextID int
}

// NewProductStore returns an empty store.
func NewProductStore() *ProductStore {
	return &ProductStore{items: map[int]model.Product{}, nextID: 1}
}

// Create stores item under the next id and returns it.
func (s *ProductStore) Create(item model.Product) model.Product {
	s.mu.Lock()
	defer s.mu.Unlock()
	item.ID = s.nextID
	s.nextID++
	s.items[item.ID] = item
	return item
}

// Get returns the record with that id.
func (s *ProductStore) Get(id int) (model.Product, bool) {
	s.mu.RLock()
	defer s.mu.RUnlock()
	item, ok := s.items[id]
	return item, ok
}

// List returns every record, oldest first.
func (s *ProductStore) List() []model.Product {
	s.mu.RLock()
	defer s.mu.RUnlock()
	out := make([]model.Product, 0, len(s.items))
	for _, item := range s.items {
		out = append(out, item)
	}
	sort.Slice(out, func(i, j int) bool { return out[i].ID < out[j].ID })
	return out
}

// Update replaces an existing record; false if there is none.
func (s *ProductStore) Update(item model.Product) bool {
	s.mu.Lock()
	defer s.mu.Unlock()
	if _, ok := s.items[item.ID]; !ok {
		return false
	}
	s.items[item.ID] = item
	return true
}

// Delete removes a record; false if there was none.
func (s *ProductStore) Delete(id int) bool {
	s.mu.Lock()
	defer s.mu.Unlock()
	if _, ok := s.items[id]; !ok {
		return false
	}
	delete(s.items, id)
	return true
}

// Count is the number of records.
func (s *ProductStore) Count() int {
	s.mu.RLock()
	defer s.mu.RUnlock()
	return len(s.items)
}

// Filter returns the records keep() accepts, oldest first.
func (s *ProductStore) Filter(keep func(model.Product) bool) []model.Product {
	out := []model.Product{}
	for _, item := range s.List() {
		if keep(item) {
			out = append(out, item)
		}
	}
	return out
}

// ForSupplier returns records linked to supplier id.
func (s *ProductStore) ForSupplier(id int) []model.Product {
	return s.Filter(func(item model.Product) bool { return item.SupplierID == id })
}

// CountForSupplier counts records linked to supplier id.
func (s *ProductStore) CountForSupplier(id int) int {
	return len(s.ForSupplier(id))
}

// FindBySku returns records whose sku is exactly value.
func (s *ProductStore) FindBySku(value string) []model.Product {
	return s.Filter(func(item model.Product) bool { return item.Sku == value })
}

// SearchSku returns records whose sku contains text (any case).
func (s *ProductStore) SearchSku(text string) []model.Product {
	needle := strings.ToLower(strings.TrimSpace(text))
	return s.Filter(func(item model.Product) bool { return strings.Contains(strings.ToLower(item.Sku), needle) })
}

// FindByName returns records whose name is exactly value.
func (s *ProductStore) FindByName(value string) []model.Product {
	return s.Filter(func(item model.Product) bool { return item.Name == value })
}

// SearchName returns records whose name contains text (any case).
func (s *ProductStore) SearchName(text string) []model.Product {
	needle := strings.ToLower(strings.TrimSpace(text))
	return s.Filter(func(item model.Product) bool { return strings.Contains(strings.ToLower(item.Name), needle) })
}

// BetweenUnitCost returns records whose unit cost is within [low, high].
func (s *ProductStore) BetweenUnitCost(low, high float64) []model.Product {
	return s.Filter(func(item model.Product) bool { return item.UnitCost >= low && item.UnitCost <= high })
}

// TotalUnitCost adds up the unit cost of every record.
func (s *ProductStore) TotalUnitCost() float64 {
	var total float64
	for _, item := range s.List() {
		total += item.UnitCost
	}
	return total
}

// AverageUnitCost is the mean unit cost (0 when there are no records).
func (s *ProductStore) AverageUnitCost() float64 {
	items := s.List()
	if len(items) == 0 {
		return 0
	}
	return float64(s.TotalUnitCost()) / float64(len(items))
}

// MaxUnitCost returns the record with the highest unit cost.
func (s *ProductStore) MaxUnitCost() (model.Product, bool) {
	var best model.Product
	found := false
	for _, item := range s.List() {
		if !found || item.UnitCost > best.UnitCost {
			best, found = item, true
		}
	}
	return best, found
}

// BetweenUnitPrice returns records whose unit price is within [low, high].
func (s *ProductStore) BetweenUnitPrice(low, high float64) []model.Product {
	return s.Filter(func(item model.Product) bool { return item.UnitPrice >= low && item.UnitPrice <= high })
}

// TotalUnitPrice adds up the unit price of every record.
func (s *ProductStore) TotalUnitPrice() float64 {
	var total float64
	for _, item := range s.List() {
		total += item.UnitPrice
	}
	return total
}

// AverageUnitPrice is the mean unit price (0 when there are no records).
func (s *ProductStore) AverageUnitPrice() float64 {
	items := s.List()
	if len(items) == 0 {
		return 0
	}
	return float64(s.TotalUnitPrice()) / float64(len(items))
}

// MaxUnitPrice returns the record with the highest unit price.
func (s *ProductStore) MaxUnitPrice() (model.Product, bool) {
	var best model.Product
	found := false
	for _, item := range s.List() {
		if !found || item.UnitPrice > best.UnitPrice {
			best, found = item, true
		}
	}
	return best, found
}

// BetweenReorderLevel returns records whose reorder level is within [low, high].
func (s *ProductStore) BetweenReorderLevel(low, high int) []model.Product {
	return s.Filter(func(item model.Product) bool { return item.ReorderLevel >= low && item.ReorderLevel <= high })
}

// TotalReorderLevel adds up the reorder level of every record.
func (s *ProductStore) TotalReorderLevel() int {
	var total int
	for _, item := range s.List() {
		total += item.ReorderLevel
	}
	return total
}

// AverageReorderLevel is the mean reorder level (0 when there are no records).
func (s *ProductStore) AverageReorderLevel() float64 {
	items := s.List()
	if len(items) == 0 {
		return 0
	}
	return float64(s.TotalReorderLevel()) / float64(len(items))
}

// MaxReorderLevel returns the record with the highest reorder level.
func (s *ProductStore) MaxReorderLevel() (model.Product, bool) {
	var best model.Product
	found := false
	for _, item := range s.List() {
		if !found || item.ReorderLevel > best.ReorderLevel {
			best, found = item, true
		}
	}
	return best, found
}

// WithCategory returns records whose category is value.
func (s *ProductStore) WithCategory(value model.ProductCategory) []model.Product {
	return s.Filter(func(item model.Product) bool { return item.Category == value })
}

// CountByCategory counts records for every category.
func (s *ProductStore) CountByCategory() map[model.ProductCategory]int {
	counts := map[model.ProductCategory]int{}
	for _, v := range model.ProductCategoryValues {
		counts[v] = 0
	}
	for _, item := range s.List() {
		counts[item.Category]++
	}
	return counts
}

// WhereActive returns records whose active flag equals flag.
func (s *ProductStore) WhereActive(flag bool) []model.Product {
	return s.Filter(func(item model.Product) bool { return item.Active == flag })
}

// Search returns records where any text field contains text (any case).
func (s *ProductStore) Search(text string) []model.Product {
	needle := strings.ToLower(strings.TrimSpace(text))
	return s.Filter(func(item model.Product) bool {
		for _, value := range []string{item.Sku, item.Name} {
			if strings.Contains(strings.ToLower(value), needle) {
				return true
			}
		}
		return false
	})
}

// BinStore keeps every bin.
type BinStore struct {
	mu     sync.RWMutex
	items  map[int]model.Bin
	nextID int
}

// NewBinStore returns an empty store.
func NewBinStore() *BinStore {
	return &BinStore{items: map[int]model.Bin{}, nextID: 1}
}

// Create stores item under the next id and returns it.
func (s *BinStore) Create(item model.Bin) model.Bin {
	s.mu.Lock()
	defer s.mu.Unlock()
	item.ID = s.nextID
	s.nextID++
	s.items[item.ID] = item
	return item
}

// Get returns the record with that id.
func (s *BinStore) Get(id int) (model.Bin, bool) {
	s.mu.RLock()
	defer s.mu.RUnlock()
	item, ok := s.items[id]
	return item, ok
}

// List returns every record, oldest first.
func (s *BinStore) List() []model.Bin {
	s.mu.RLock()
	defer s.mu.RUnlock()
	out := make([]model.Bin, 0, len(s.items))
	for _, item := range s.items {
		out = append(out, item)
	}
	sort.Slice(out, func(i, j int) bool { return out[i].ID < out[j].ID })
	return out
}

// Update replaces an existing record; false if there is none.
func (s *BinStore) Update(item model.Bin) bool {
	s.mu.Lock()
	defer s.mu.Unlock()
	if _, ok := s.items[item.ID]; !ok {
		return false
	}
	s.items[item.ID] = item
	return true
}

// Delete removes a record; false if there was none.
func (s *BinStore) Delete(id int) bool {
	s.mu.Lock()
	defer s.mu.Unlock()
	if _, ok := s.items[id]; !ok {
		return false
	}
	delete(s.items, id)
	return true
}

// Count is the number of records.
func (s *BinStore) Count() int {
	s.mu.RLock()
	defer s.mu.RUnlock()
	return len(s.items)
}

// Filter returns the records keep() accepts, oldest first.
func (s *BinStore) Filter(keep func(model.Bin) bool) []model.Bin {
	out := []model.Bin{}
	for _, item := range s.List() {
		if keep(item) {
			out = append(out, item)
		}
	}
	return out
}

// FindByCode returns records whose code is exactly value.
func (s *BinStore) FindByCode(value string) []model.Bin {
	return s.Filter(func(item model.Bin) bool { return item.Code == value })
}

// SearchCode returns records whose code contains text (any case).
func (s *BinStore) SearchCode(text string) []model.Bin {
	needle := strings.ToLower(strings.TrimSpace(text))
	return s.Filter(func(item model.Bin) bool { return strings.Contains(strings.ToLower(item.Code), needle) })
}

// FindByAisle returns records whose aisle is exactly value.
func (s *BinStore) FindByAisle(value string) []model.Bin {
	return s.Filter(func(item model.Bin) bool { return item.Aisle == value })
}

// SearchAisle returns records whose aisle contains text (any case).
func (s *BinStore) SearchAisle(text string) []model.Bin {
	needle := strings.ToLower(strings.TrimSpace(text))
	return s.Filter(func(item model.Bin) bool { return strings.Contains(strings.ToLower(item.Aisle), needle) })
}

// BetweenShelf returns records whose shelf is within [low, high].
func (s *BinStore) BetweenShelf(low, high int) []model.Bin {
	return s.Filter(func(item model.Bin) bool { return item.Shelf >= low && item.Shelf <= high })
}

// TotalShelf adds up the shelf of every record.
func (s *BinStore) TotalShelf() int {
	var total int
	for _, item := range s.List() {
		total += item.Shelf
	}
	return total
}

// AverageShelf is the mean shelf (0 when there are no records).
func (s *BinStore) AverageShelf() float64 {
	items := s.List()
	if len(items) == 0 {
		return 0
	}
	return float64(s.TotalShelf()) / float64(len(items))
}

// MaxShelf returns the record with the highest shelf.
func (s *BinStore) MaxShelf() (model.Bin, bool) {
	var best model.Bin
	found := false
	for _, item := range s.List() {
		if !found || item.Shelf > best.Shelf {
			best, found = item, true
		}
	}
	return best, found
}

// BetweenCapacity returns records whose capacity is within [low, high].
func (s *BinStore) BetweenCapacity(low, high int) []model.Bin {
	return s.Filter(func(item model.Bin) bool { return item.Capacity >= low && item.Capacity <= high })
}

// TotalCapacity adds up the capacity of every record.
func (s *BinStore) TotalCapacity() int {
	var total int
	for _, item := range s.List() {
		total += item.Capacity
	}
	return total
}

// AverageCapacity is the mean capacity (0 when there are no records).
func (s *BinStore) AverageCapacity() float64 {
	items := s.List()
	if len(items) == 0 {
		return 0
	}
	return float64(s.TotalCapacity()) / float64(len(items))
}

// MaxCapacity returns the record with the highest capacity.
func (s *BinStore) MaxCapacity() (model.Bin, bool) {
	var best model.Bin
	found := false
	for _, item := range s.List() {
		if !found || item.Capacity > best.Capacity {
			best, found = item, true
		}
	}
	return best, found
}

// WhereRefrigerated returns records whose refrigerated flag equals flag.
func (s *BinStore) WhereRefrigerated(flag bool) []model.Bin {
	return s.Filter(func(item model.Bin) bool { return item.Refrigerated == flag })
}

// Search returns records where any text field contains text (any case).
func (s *BinStore) Search(text string) []model.Bin {
	needle := strings.ToLower(strings.TrimSpace(text))
	return s.Filter(func(item model.Bin) bool {
		for _, value := range []string{item.Code, item.Aisle} {
			if strings.Contains(strings.ToLower(value), needle) {
				return true
			}
		}
		return false
	})
}

// StockMovementStore keeps every stock movement.
type StockMovementStore struct {
	mu     sync.RWMutex
	items  map[int]model.StockMovement
	nextID int
}

// NewStockMovementStore returns an empty store.
func NewStockMovementStore() *StockMovementStore {
	return &StockMovementStore{items: map[int]model.StockMovement{}, nextID: 1}
}

// Create stores item under the next id and returns it.
func (s *StockMovementStore) Create(item model.StockMovement) model.StockMovement {
	s.mu.Lock()
	defer s.mu.Unlock()
	item.ID = s.nextID
	s.nextID++
	s.items[item.ID] = item
	return item
}

// Get returns the record with that id.
func (s *StockMovementStore) Get(id int) (model.StockMovement, bool) {
	s.mu.RLock()
	defer s.mu.RUnlock()
	item, ok := s.items[id]
	return item, ok
}

// List returns every record, oldest first.
func (s *StockMovementStore) List() []model.StockMovement {
	s.mu.RLock()
	defer s.mu.RUnlock()
	out := make([]model.StockMovement, 0, len(s.items))
	for _, item := range s.items {
		out = append(out, item)
	}
	sort.Slice(out, func(i, j int) bool { return out[i].ID < out[j].ID })
	return out
}

// Update replaces an existing record; false if there is none.
func (s *StockMovementStore) Update(item model.StockMovement) bool {
	s.mu.Lock()
	defer s.mu.Unlock()
	if _, ok := s.items[item.ID]; !ok {
		return false
	}
	s.items[item.ID] = item
	return true
}

// Delete removes a record; false if there was none.
func (s *StockMovementStore) Delete(id int) bool {
	s.mu.Lock()
	defer s.mu.Unlock()
	if _, ok := s.items[id]; !ok {
		return false
	}
	delete(s.items, id)
	return true
}

// Count is the number of records.
func (s *StockMovementStore) Count() int {
	s.mu.RLock()
	defer s.mu.RUnlock()
	return len(s.items)
}

// Filter returns the records keep() accepts, oldest first.
func (s *StockMovementStore) Filter(keep func(model.StockMovement) bool) []model.StockMovement {
	out := []model.StockMovement{}
	for _, item := range s.List() {
		if keep(item) {
			out = append(out, item)
		}
	}
	return out
}

// ForProduct returns records linked to product id.
func (s *StockMovementStore) ForProduct(id int) []model.StockMovement {
	return s.Filter(func(item model.StockMovement) bool { return item.ProductID == id })
}

// CountForProduct counts records linked to product id.
func (s *StockMovementStore) CountForProduct(id int) int {
	return len(s.ForProduct(id))
}

// ForBin returns records linked to bin id.
func (s *StockMovementStore) ForBin(id int) []model.StockMovement {
	return s.Filter(func(item model.StockMovement) bool { return item.BinID == id })
}

// CountForBin counts records linked to bin id.
func (s *StockMovementStore) CountForBin(id int) int {
	return len(s.ForBin(id))
}

// BetweenQuantity returns records whose quantity is within [low, high].
func (s *StockMovementStore) BetweenQuantity(low, high int) []model.StockMovement {
	return s.Filter(func(item model.StockMovement) bool { return item.Quantity >= low && item.Quantity <= high })
}

// TotalQuantity adds up the quantity of every record.
func (s *StockMovementStore) TotalQuantity() int {
	var total int
	for _, item := range s.List() {
		total += item.Quantity
	}
	return total
}

// AverageQuantity is the mean quantity (0 when there are no records).
func (s *StockMovementStore) AverageQuantity() float64 {
	items := s.List()
	if len(items) == 0 {
		return 0
	}
	return float64(s.TotalQuantity()) / float64(len(items))
}

// MaxQuantity returns the record with the highest quantity.
func (s *StockMovementStore) MaxQuantity() (model.StockMovement, bool) {
	var best model.StockMovement
	found := false
	for _, item := range s.List() {
		if !found || item.Quantity > best.Quantity {
			best, found = item, true
		}
	}
	return best, found
}

// MovedBefore returns records whose moved is before day (YYYY-MM-DD).
func (s *StockMovementStore) MovedBefore(day string) []model.StockMovement {
	return s.Filter(func(item model.StockMovement) bool { return item.Moved < day })
}

// MovedAfter returns records whose moved is after day (YYYY-MM-DD).
func (s *StockMovementStore) MovedAfter(day string) []model.StockMovement {
	return s.Filter(func(item model.StockMovement) bool { return item.Moved > day })
}

// MovedOn returns records whose moved is day.
func (s *StockMovementStore) MovedOn(day string) []model.StockMovement {
	return s.Filter(func(item model.StockMovement) bool { return item.Moved == day })
}

// WithReason returns records whose reason is value.
func (s *StockMovementStore) WithReason(value model.StockMovementReason) []model.StockMovement {
	return s.Filter(func(item model.StockMovement) bool { return item.Reason == value })
}

// CountByReason counts records for every reason.
func (s *StockMovementStore) CountByReason() map[model.StockMovementReason]int {
	counts := map[model.StockMovementReason]int{}
	for _, v := range model.StockMovementReasonValues {
		counts[v] = 0
	}
	for _, item := range s.List() {
		counts[item.Reason]++
	}
	return counts
}

// FindByReference returns records whose reference is exactly value.
func (s *StockMovementStore) FindByReference(value string) []model.StockMovement {
	return s.Filter(func(item model.StockMovement) bool { return item.Reference == value })
}

// SearchReference returns records whose reference contains text (any case).
func (s *StockMovementStore) SearchReference(text string) []model.StockMovement {
	needle := strings.ToLower(strings.TrimSpace(text))
	return s.Filter(func(item model.StockMovement) bool { return strings.Contains(strings.ToLower(item.Reference), needle) })
}

// Search returns records where any text field contains text (any case).
func (s *StockMovementStore) Search(text string) []model.StockMovement {
	needle := strings.ToLower(strings.TrimSpace(text))
	return s.Filter(func(item model.StockMovement) bool {
		for _, value := range []string{item.Reference} {
			if strings.Contains(strings.ToLower(value), needle) {
				return true
			}
		}
		return false
	})
}

// PurchaseOrderStore keeps every purchase order.
type PurchaseOrderStore struct {
	mu     sync.RWMutex
	items  map[int]model.PurchaseOrder
	nextID int
}

// NewPurchaseOrderStore returns an empty store.
func NewPurchaseOrderStore() *PurchaseOrderStore {
	return &PurchaseOrderStore{items: map[int]model.PurchaseOrder{}, nextID: 1}
}

// Create stores item under the next id and returns it.
func (s *PurchaseOrderStore) Create(item model.PurchaseOrder) model.PurchaseOrder {
	s.mu.Lock()
	defer s.mu.Unlock()
	item.ID = s.nextID
	s.nextID++
	s.items[item.ID] = item
	return item
}

// Get returns the record with that id.
func (s *PurchaseOrderStore) Get(id int) (model.PurchaseOrder, bool) {
	s.mu.RLock()
	defer s.mu.RUnlock()
	item, ok := s.items[id]
	return item, ok
}

// List returns every record, oldest first.
func (s *PurchaseOrderStore) List() []model.PurchaseOrder {
	s.mu.RLock()
	defer s.mu.RUnlock()
	out := make([]model.PurchaseOrder, 0, len(s.items))
	for _, item := range s.items {
		out = append(out, item)
	}
	sort.Slice(out, func(i, j int) bool { return out[i].ID < out[j].ID })
	return out
}

// Update replaces an existing record; false if there is none.
func (s *PurchaseOrderStore) Update(item model.PurchaseOrder) bool {
	s.mu.Lock()
	defer s.mu.Unlock()
	if _, ok := s.items[item.ID]; !ok {
		return false
	}
	s.items[item.ID] = item
	return true
}

// Delete removes a record; false if there was none.
func (s *PurchaseOrderStore) Delete(id int) bool {
	s.mu.Lock()
	defer s.mu.Unlock()
	if _, ok := s.items[id]; !ok {
		return false
	}
	delete(s.items, id)
	return true
}

// Count is the number of records.
func (s *PurchaseOrderStore) Count() int {
	s.mu.RLock()
	defer s.mu.RUnlock()
	return len(s.items)
}

// Filter returns the records keep() accepts, oldest first.
func (s *PurchaseOrderStore) Filter(keep func(model.PurchaseOrder) bool) []model.PurchaseOrder {
	out := []model.PurchaseOrder{}
	for _, item := range s.List() {
		if keep(item) {
			out = append(out, item)
		}
	}
	return out
}

// ForSupplier returns records linked to supplier id.
func (s *PurchaseOrderStore) ForSupplier(id int) []model.PurchaseOrder {
	return s.Filter(func(item model.PurchaseOrder) bool { return item.SupplierID == id })
}

// CountForSupplier counts records linked to supplier id.
func (s *PurchaseOrderStore) CountForSupplier(id int) int {
	return len(s.ForSupplier(id))
}

// OrderedBefore returns records whose ordered is before day (YYYY-MM-DD).
func (s *PurchaseOrderStore) OrderedBefore(day string) []model.PurchaseOrder {
	return s.Filter(func(item model.PurchaseOrder) bool { return item.Ordered < day })
}

// OrderedAfter returns records whose ordered is after day (YYYY-MM-DD).
func (s *PurchaseOrderStore) OrderedAfter(day string) []model.PurchaseOrder {
	return s.Filter(func(item model.PurchaseOrder) bool { return item.Ordered > day })
}

// OrderedOn returns records whose ordered is day.
func (s *PurchaseOrderStore) OrderedOn(day string) []model.PurchaseOrder {
	return s.Filter(func(item model.PurchaseOrder) bool { return item.Ordered == day })
}

// ExpectedBefore returns records whose expected is before day (YYYY-MM-DD).
func (s *PurchaseOrderStore) ExpectedBefore(day string) []model.PurchaseOrder {
	return s.Filter(func(item model.PurchaseOrder) bool { return item.Expected < day })
}

// ExpectedAfter returns records whose expected is after day (YYYY-MM-DD).
func (s *PurchaseOrderStore) ExpectedAfter(day string) []model.PurchaseOrder {
	return s.Filter(func(item model.PurchaseOrder) bool { return item.Expected > day })
}

// ExpectedOn returns records whose expected is day.
func (s *PurchaseOrderStore) ExpectedOn(day string) []model.PurchaseOrder {
	return s.Filter(func(item model.PurchaseOrder) bool { return item.Expected == day })
}

// BetweenTotal returns records whose total is within [low, high].
func (s *PurchaseOrderStore) BetweenTotal(low, high float64) []model.PurchaseOrder {
	return s.Filter(func(item model.PurchaseOrder) bool { return item.Total >= low && item.Total <= high })
}

// TotalTotal adds up the total of every record.
func (s *PurchaseOrderStore) TotalTotal() float64 {
	var total float64
	for _, item := range s.List() {
		total += item.Total
	}
	return total
}

// AverageTotal is the mean total (0 when there are no records).
func (s *PurchaseOrderStore) AverageTotal() float64 {
	items := s.List()
	if len(items) == 0 {
		return 0
	}
	return float64(s.TotalTotal()) / float64(len(items))
}

// MaxTotal returns the record with the highest total.
func (s *PurchaseOrderStore) MaxTotal() (model.PurchaseOrder, bool) {
	var best model.PurchaseOrder
	found := false
	for _, item := range s.List() {
		if !found || item.Total > best.Total {
			best, found = item, true
		}
	}
	return best, found
}

// WithStatus returns records whose status is value.
func (s *PurchaseOrderStore) WithStatus(value model.PurchaseOrderStatus) []model.PurchaseOrder {
	return s.Filter(func(item model.PurchaseOrder) bool { return item.Status == value })
}

// CountByStatus counts records for every status.
func (s *PurchaseOrderStore) CountByStatus() map[model.PurchaseOrderStatus]int {
	counts := map[model.PurchaseOrderStatus]int{}
	for _, v := range model.PurchaseOrderStatusValues {
		counts[v] = 0
	}
	for _, item := range s.List() {
		counts[item.Status]++
	}
	return counts
}

// FindByNotes returns records whose notes is exactly value.
func (s *PurchaseOrderStore) FindByNotes(value string) []model.PurchaseOrder {
	return s.Filter(func(item model.PurchaseOrder) bool { return item.Notes == value })
}

// SearchNotes returns records whose notes contains text (any case).
func (s *PurchaseOrderStore) SearchNotes(text string) []model.PurchaseOrder {
	needle := strings.ToLower(strings.TrimSpace(text))
	return s.Filter(func(item model.PurchaseOrder) bool { return strings.Contains(strings.ToLower(item.Notes), needle) })
}

// Search returns records where any text field contains text (any case).
func (s *PurchaseOrderStore) Search(text string) []model.PurchaseOrder {
	needle := strings.ToLower(strings.TrimSpace(text))
	return s.Filter(func(item model.PurchaseOrder) bool {
		for _, value := range []string{item.Notes} {
			if strings.Contains(strings.ToLower(value), needle) {
				return true
			}
		}
		return false
	})
}

// StockCountStore keeps every stock count.
type StockCountStore struct {
	mu     sync.RWMutex
	items  map[int]model.StockCount
	nextID int
}

// NewStockCountStore returns an empty store.
func NewStockCountStore() *StockCountStore {
	return &StockCountStore{items: map[int]model.StockCount{}, nextID: 1}
}

// Create stores item under the next id and returns it.
func (s *StockCountStore) Create(item model.StockCount) model.StockCount {
	s.mu.Lock()
	defer s.mu.Unlock()
	item.ID = s.nextID
	s.nextID++
	s.items[item.ID] = item
	return item
}

// Get returns the record with that id.
func (s *StockCountStore) Get(id int) (model.StockCount, bool) {
	s.mu.RLock()
	defer s.mu.RUnlock()
	item, ok := s.items[id]
	return item, ok
}

// List returns every record, oldest first.
func (s *StockCountStore) List() []model.StockCount {
	s.mu.RLock()
	defer s.mu.RUnlock()
	out := make([]model.StockCount, 0, len(s.items))
	for _, item := range s.items {
		out = append(out, item)
	}
	sort.Slice(out, func(i, j int) bool { return out[i].ID < out[j].ID })
	return out
}

// Update replaces an existing record; false if there is none.
func (s *StockCountStore) Update(item model.StockCount) bool {
	s.mu.Lock()
	defer s.mu.Unlock()
	if _, ok := s.items[item.ID]; !ok {
		return false
	}
	s.items[item.ID] = item
	return true
}

// Delete removes a record; false if there was none.
func (s *StockCountStore) Delete(id int) bool {
	s.mu.Lock()
	defer s.mu.Unlock()
	if _, ok := s.items[id]; !ok {
		return false
	}
	delete(s.items, id)
	return true
}

// Count is the number of records.
func (s *StockCountStore) Count() int {
	s.mu.RLock()
	defer s.mu.RUnlock()
	return len(s.items)
}

// Filter returns the records keep() accepts, oldest first.
func (s *StockCountStore) Filter(keep func(model.StockCount) bool) []model.StockCount {
	out := []model.StockCount{}
	for _, item := range s.List() {
		if keep(item) {
			out = append(out, item)
		}
	}
	return out
}

// ForBin returns records linked to bin id.
func (s *StockCountStore) ForBin(id int) []model.StockCount {
	return s.Filter(func(item model.StockCount) bool { return item.BinID == id })
}

// CountForBin counts records linked to bin id.
func (s *StockCountStore) CountForBin(id int) int {
	return len(s.ForBin(id))
}

// ForProduct returns records linked to product id.
func (s *StockCountStore) ForProduct(id int) []model.StockCount {
	return s.Filter(func(item model.StockCount) bool { return item.ProductID == id })
}

// CountForProduct counts records linked to product id.
func (s *StockCountStore) CountForProduct(id int) int {
	return len(s.ForProduct(id))
}

// CountedBefore returns records whose counted is before day (YYYY-MM-DD).
func (s *StockCountStore) CountedBefore(day string) []model.StockCount {
	return s.Filter(func(item model.StockCount) bool { return item.Counted < day })
}

// CountedAfter returns records whose counted is after day (YYYY-MM-DD).
func (s *StockCountStore) CountedAfter(day string) []model.StockCount {
	return s.Filter(func(item model.StockCount) bool { return item.Counted > day })
}

// CountedOn returns records whose counted is day.
func (s *StockCountStore) CountedOn(day string) []model.StockCount {
	return s.Filter(func(item model.StockCount) bool { return item.Counted == day })
}

// BetweenExpected returns records whose expected is within [low, high].
func (s *StockCountStore) BetweenExpected(low, high int) []model.StockCount {
	return s.Filter(func(item model.StockCount) bool { return item.Expected >= low && item.Expected <= high })
}

// TotalExpected adds up the expected of every record.
func (s *StockCountStore) TotalExpected() int {
	var total int
	for _, item := range s.List() {
		total += item.Expected
	}
	return total
}

// AverageExpected is the mean expected (0 when there are no records).
func (s *StockCountStore) AverageExpected() float64 {
	items := s.List()
	if len(items) == 0 {
		return 0
	}
	return float64(s.TotalExpected()) / float64(len(items))
}

// MaxExpected returns the record with the highest expected.
func (s *StockCountStore) MaxExpected() (model.StockCount, bool) {
	var best model.StockCount
	found := false
	for _, item := range s.List() {
		if !found || item.Expected > best.Expected {
			best, found = item, true
		}
	}
	return best, found
}

// BetweenFound returns records whose found is within [low, high].
func (s *StockCountStore) BetweenFound(low, high int) []model.StockCount {
	return s.Filter(func(item model.StockCount) bool { return item.Found >= low && item.Found <= high })
}

// TotalFound adds up the found of every record.
func (s *StockCountStore) TotalFound() int {
	var total int
	for _, item := range s.List() {
		total += item.Found
	}
	return total
}

// AverageFound is the mean found (0 when there are no records).
func (s *StockCountStore) AverageFound() float64 {
	items := s.List()
	if len(items) == 0 {
		return 0
	}
	return float64(s.TotalFound()) / float64(len(items))
}

// MaxFound returns the record with the highest found.
func (s *StockCountStore) MaxFound() (model.StockCount, bool) {
	var best model.StockCount
	found := false
	for _, item := range s.List() {
		if !found || item.Found > best.Found {
			best, found = item, true
		}
	}
	return best, found
}

// FindByCounter returns records whose counter is exactly value.
func (s *StockCountStore) FindByCounter(value string) []model.StockCount {
	return s.Filter(func(item model.StockCount) bool { return item.Counter == value })
}

// SearchCounter returns records whose counter contains text (any case).
func (s *StockCountStore) SearchCounter(text string) []model.StockCount {
	needle := strings.ToLower(strings.TrimSpace(text))
	return s.Filter(func(item model.StockCount) bool { return strings.Contains(strings.ToLower(item.Counter), needle) })
}

// Search returns records where any text field contains text (any case).
func (s *StockCountStore) Search(text string) []model.StockCount {
	needle := strings.ToLower(strings.TrimSpace(text))
	return s.Filter(func(item model.StockCount) bool {
		for _, value := range []string{item.Counter} {
			if strings.Contains(strings.ToLower(value), needle) {
				return true
			}
		}
		return false
	})
}

// DocumentStore keeps every document.
type DocumentStore struct {
	mu     sync.RWMutex
	items  map[int]model.Document
	nextID int
}

// NewDocumentStore returns an empty store.
func NewDocumentStore() *DocumentStore {
	return &DocumentStore{items: map[int]model.Document{}, nextID: 1}
}

// Create stores item under the next id and returns it.
func (s *DocumentStore) Create(item model.Document) model.Document {
	s.mu.Lock()
	defer s.mu.Unlock()
	item.ID = s.nextID
	s.nextID++
	s.items[item.ID] = item
	return item
}

// Get returns the record with that id.
func (s *DocumentStore) Get(id int) (model.Document, bool) {
	s.mu.RLock()
	defer s.mu.RUnlock()
	item, ok := s.items[id]
	return item, ok
}

// List returns every record, oldest first.
func (s *DocumentStore) List() []model.Document {
	s.mu.RLock()
	defer s.mu.RUnlock()
	out := make([]model.Document, 0, len(s.items))
	for _, item := range s.items {
		out = append(out, item)
	}
	sort.Slice(out, func(i, j int) bool { return out[i].ID < out[j].ID })
	return out
}

// Update replaces an existing record; false if there is none.
func (s *DocumentStore) Update(item model.Document) bool {
	s.mu.Lock()
	defer s.mu.Unlock()
	if _, ok := s.items[item.ID]; !ok {
		return false
	}
	s.items[item.ID] = item
	return true
}

// Delete removes a record; false if there was none.
func (s *DocumentStore) Delete(id int) bool {
	s.mu.Lock()
	defer s.mu.Unlock()
	if _, ok := s.items[id]; !ok {
		return false
	}
	delete(s.items, id)
	return true
}

// Count is the number of records.
func (s *DocumentStore) Count() int {
	s.mu.RLock()
	defer s.mu.RUnlock()
	return len(s.items)
}

// Filter returns the records keep() accepts, oldest first.
func (s *DocumentStore) Filter(keep func(model.Document) bool) []model.Document {
	out := []model.Document{}
	for _, item := range s.List() {
		if keep(item) {
			out = append(out, item)
		}
	}
	return out
}

// ForSupplier returns records linked to supplier id.
func (s *DocumentStore) ForSupplier(id int) []model.Document {
	return s.Filter(func(item model.Document) bool { return item.SupplierID == id })
}

// CountForSupplier counts records linked to supplier id.
func (s *DocumentStore) CountForSupplier(id int) int {
	return len(s.ForSupplier(id))
}

// FindByTitle returns records whose title is exactly value.
func (s *DocumentStore) FindByTitle(value string) []model.Document {
	return s.Filter(func(item model.Document) bool { return item.Title == value })
}

// SearchTitle returns records whose title contains text (any case).
func (s *DocumentStore) SearchTitle(text string) []model.Document {
	needle := strings.ToLower(strings.TrimSpace(text))
	return s.Filter(func(item model.Document) bool { return strings.Contains(strings.ToLower(item.Title), needle) })
}

// BetweenPages returns records whose pages is within [low, high].
func (s *DocumentStore) BetweenPages(low, high int) []model.Document {
	return s.Filter(func(item model.Document) bool { return item.Pages >= low && item.Pages <= high })
}

// TotalPages adds up the pages of every record.
func (s *DocumentStore) TotalPages() int {
	var total int
	for _, item := range s.List() {
		total += item.Pages
	}
	return total
}

// AveragePages is the mean pages (0 when there are no records).
func (s *DocumentStore) AveragePages() float64 {
	items := s.List()
	if len(items) == 0 {
		return 0
	}
	return float64(s.TotalPages()) / float64(len(items))
}

// MaxPages returns the record with the highest pages.
func (s *DocumentStore) MaxPages() (model.Document, bool) {
	var best model.Document
	found := false
	for _, item := range s.List() {
		if !found || item.Pages > best.Pages {
			best, found = item, true
		}
	}
	return best, found
}

// WhereSigned returns records whose signed flag equals flag.
func (s *DocumentStore) WhereSigned(flag bool) []model.Document {
	return s.Filter(func(item model.Document) bool { return item.Signed == flag })
}

// BetweenVersion returns records whose version is within [low, high].
func (s *DocumentStore) BetweenVersion(low, high int) []model.Document {
	return s.Filter(func(item model.Document) bool { return item.Version >= low && item.Version <= high })
}

// TotalVersion adds up the version of every record.
func (s *DocumentStore) TotalVersion() int {
	var total int
	for _, item := range s.List() {
		total += item.Version
	}
	return total
}

// AverageVersion is the mean version (0 when there are no records).
func (s *DocumentStore) AverageVersion() float64 {
	items := s.List()
	if len(items) == 0 {
		return 0
	}
	return float64(s.TotalVersion()) / float64(len(items))
}

// MaxVersion returns the record with the highest version.
func (s *DocumentStore) MaxVersion() (model.Document, bool) {
	var best model.Document
	found := false
	for _, item := range s.List() {
		if !found || item.Version > best.Version {
			best, found = item, true
		}
	}
	return best, found
}

// IssuedBefore returns records whose issued is before day (YYYY-MM-DD).
func (s *DocumentStore) IssuedBefore(day string) []model.Document {
	return s.Filter(func(item model.Document) bool { return item.Issued < day })
}

// IssuedAfter returns records whose issued is after day (YYYY-MM-DD).
func (s *DocumentStore) IssuedAfter(day string) []model.Document {
	return s.Filter(func(item model.Document) bool { return item.Issued > day })
}

// IssuedOn returns records whose issued is day.
func (s *DocumentStore) IssuedOn(day string) []model.Document {
	return s.Filter(func(item model.Document) bool { return item.Issued == day })
}

// Search returns records where any text field contains text (any case).
func (s *DocumentStore) Search(text string) []model.Document {
	needle := strings.ToLower(strings.TrimSpace(text))
	return s.Filter(func(item model.Document) bool {
		for _, value := range []string{item.Title} {
			if strings.Contains(strings.ToLower(value), needle) {
				return true
			}
		}
		return false
	})
}

// NotificationStore keeps every notification.
type NotificationStore struct {
	mu     sync.RWMutex
	items  map[int]model.Notification
	nextID int
}

// NewNotificationStore returns an empty store.
func NewNotificationStore() *NotificationStore {
	return &NotificationStore{items: map[int]model.Notification{}, nextID: 1}
}

// Create stores item under the next id and returns it.
func (s *NotificationStore) Create(item model.Notification) model.Notification {
	s.mu.Lock()
	defer s.mu.Unlock()
	item.ID = s.nextID
	s.nextID++
	s.items[item.ID] = item
	return item
}

// Get returns the record with that id.
func (s *NotificationStore) Get(id int) (model.Notification, bool) {
	s.mu.RLock()
	defer s.mu.RUnlock()
	item, ok := s.items[id]
	return item, ok
}

// List returns every record, oldest first.
func (s *NotificationStore) List() []model.Notification {
	s.mu.RLock()
	defer s.mu.RUnlock()
	out := make([]model.Notification, 0, len(s.items))
	for _, item := range s.items {
		out = append(out, item)
	}
	sort.Slice(out, func(i, j int) bool { return out[i].ID < out[j].ID })
	return out
}

// Update replaces an existing record; false if there is none.
func (s *NotificationStore) Update(item model.Notification) bool {
	s.mu.Lock()
	defer s.mu.Unlock()
	if _, ok := s.items[item.ID]; !ok {
		return false
	}
	s.items[item.ID] = item
	return true
}

// Delete removes a record; false if there was none.
func (s *NotificationStore) Delete(id int) bool {
	s.mu.Lock()
	defer s.mu.Unlock()
	if _, ok := s.items[id]; !ok {
		return false
	}
	delete(s.items, id)
	return true
}

// Count is the number of records.
func (s *NotificationStore) Count() int {
	s.mu.RLock()
	defer s.mu.RUnlock()
	return len(s.items)
}

// Filter returns the records keep() accepts, oldest first.
func (s *NotificationStore) Filter(keep func(model.Notification) bool) []model.Notification {
	out := []model.Notification{}
	for _, item := range s.List() {
		if keep(item) {
			out = append(out, item)
		}
	}
	return out
}

// FindByRecipient returns records whose recipient is exactly value.
func (s *NotificationStore) FindByRecipient(value string) []model.Notification {
	return s.Filter(func(item model.Notification) bool { return item.Recipient == value })
}

// SearchRecipient returns records whose recipient contains text (any case).
func (s *NotificationStore) SearchRecipient(text string) []model.Notification {
	needle := strings.ToLower(strings.TrimSpace(text))
	return s.Filter(func(item model.Notification) bool { return strings.Contains(strings.ToLower(item.Recipient), needle) })
}

// FindByTitle returns records whose title is exactly value.
func (s *NotificationStore) FindByTitle(value string) []model.Notification {
	return s.Filter(func(item model.Notification) bool { return item.Title == value })
}

// SearchTitle returns records whose title contains text (any case).
func (s *NotificationStore) SearchTitle(text string) []model.Notification {
	needle := strings.ToLower(strings.TrimSpace(text))
	return s.Filter(func(item model.Notification) bool { return strings.Contains(strings.ToLower(item.Title), needle) })
}

// SentBefore returns records whose sent is before day (YYYY-MM-DD).
func (s *NotificationStore) SentBefore(day string) []model.Notification {
	return s.Filter(func(item model.Notification) bool { return item.Sent < day })
}

// SentAfter returns records whose sent is after day (YYYY-MM-DD).
func (s *NotificationStore) SentAfter(day string) []model.Notification {
	return s.Filter(func(item model.Notification) bool { return item.Sent > day })
}

// SentOn returns records whose sent is day.
func (s *NotificationStore) SentOn(day string) []model.Notification {
	return s.Filter(func(item model.Notification) bool { return item.Sent == day })
}

// WithChannel returns records whose channel is value.
func (s *NotificationStore) WithChannel(value model.NotificationChannel) []model.Notification {
	return s.Filter(func(item model.Notification) bool { return item.Channel == value })
}

// CountByChannel counts records for every channel.
func (s *NotificationStore) CountByChannel() map[model.NotificationChannel]int {
	counts := map[model.NotificationChannel]int{}
	for _, v := range model.NotificationChannelValues {
		counts[v] = 0
	}
	for _, item := range s.List() {
		counts[item.Channel]++
	}
	return counts
}

// WhereRead returns records whose read flag equals flag.
func (s *NotificationStore) WhereRead(flag bool) []model.Notification {
	return s.Filter(func(item model.Notification) bool { return item.Read == flag })
}

// Search returns records where any text field contains text (any case).
func (s *NotificationStore) Search(text string) []model.Notification {
	needle := strings.ToLower(strings.TrimSpace(text))
	return s.Filter(func(item model.Notification) bool {
		for _, value := range []string{item.Recipient, item.Title} {
			if strings.Contains(strings.ToLower(value), needle) {
				return true
			}
		}
		return false
	})
}
