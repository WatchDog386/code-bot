// Package model holds the Warehouse Inventory records and their validation rules.
package model

import (
	"cmp"
	"errors"
	"fmt"
	"math"
	"regexp"
	"strings"
	"time"
)

var emailPattern = regexp.MustCompile(`^[^@\s]+@[^@\s]+\.[^@\s]+$`)

// ValidationError reports a field holding a value the service can't accept.
type ValidationError struct {
	Field   string
	Message string
}

func (e *ValidationError) Error() string { return e.Field + ": " + e.Message }

// Invalid builds a ValidationError.
func Invalid(field, format string, args ...any) error {
	return &ValidationError{Field: field, Message: fmt.Sprintf(format, args...)}
}

// IsValidation reports whether err is (or wraps) a ValidationError.
func IsValidation(err error) bool {
	var v *ValidationError
	return errors.As(err, &v)
}

// CheckText trims value and checks it isn't empty (unless optional) or too long.
func CheckText(field, value string, max int, required bool) (string, error) {
	cleaned := strings.TrimSpace(value)
	if required && cleaned == "" {
		return "", Invalid(field, "is required")
	}
	if len(cleaned) > max {
		return "", Invalid(field, "must be at most %d characters", max)
	}
	return cleaned, nil
}

// CheckEmail checks for a plausible e-mail address and lower-cases it.
func CheckEmail(field, value string) (string, error) {
	text, err := CheckText(field, value, 254, true)
	if err != nil {
		return "", err
	}
	if !emailPattern.MatchString(text) {
		return "", Invalid(field, "must be an e-mail address")
	}
	return strings.ToLower(text), nil
}

// CheckInt rejects negative numbers.
func CheckInt(field string, value int) error {
	if value < 0 {
		return Invalid(field, "must be at least 0")
	}
	if value > 1_000_000_000 {
		return Invalid(field, "must be at most 1000000000")
	}
	return nil
}

// CheckNumber rejects negative amounts.
func CheckNumber(field string, value float64) error {
	if value < 0 {
		return Invalid(field, "must be at least 0")
	}
	return nil
}

// CheckDate wants an ISO date (YYYY-MM-DD) that exists in the calendar.
func CheckDate(field, value string) error {
	if _, err := time.Parse("2006-01-02", value); err != nil {
		return Invalid(field, "must be a real date like 2026-01-31")
	}
	return nil
}

// CheckRef wants the id of another record (existence is checked by the service).
func CheckRef(field string, value int) error {
	if value < 1 {
		return Invalid(field, "must point at a record")
	}
	return nil
}

// ProductCategory is the category of a Product.
type ProductCategory string

// Allowed ProductCategory values.
const (
	ProductCategoryHardware   ProductCategory = "hardware"
	ProductCategoryElectrical ProductCategory = "electrical"
	ProductCategoryPlumbing   ProductCategory = "plumbing"
	ProductCategoryTools      ProductCategory = "tools"
	ProductCategorySafety     ProductCategory = "safety"
)

// ProductCategoryValues lists every allowed ProductCategory.
var ProductCategoryValues = []ProductCategory{ProductCategoryHardware, ProductCategoryElectrical, ProductCategoryPlumbing, ProductCategoryTools, ProductCategorySafety}

// Valid reports whether v is one of the allowed values.
func (v ProductCategory) Valid() bool {
	for _, allowed := range ProductCategoryValues {
		if v == allowed {
			return true
		}
	}
	return false
}

// Label is a human-friendly name for v.
func (v ProductCategory) Label() string {
	text := strings.ReplaceAll(string(v), "_", " ")
	return strings.ToUpper(text[:1]) + text[1:]
}

// ParseProductCategory turns text into a ProductCategory.
func ParseProductCategory(text string) (ProductCategory, error) {
	v := ProductCategory(strings.ToLower(strings.TrimSpace(text)))
	if !v.Valid() {
		return "", Invalid("category", "must be one of %s", ProductCategoryList())
	}
	return v, nil
}

// ProductCategoryList is every allowed value, comma separated.
func ProductCategoryList() string {
	parts := make([]string, len(ProductCategoryValues))
	for i, v := range ProductCategoryValues {
		parts[i] = string(v)
	}
	return strings.Join(parts, ", ")
}

// StockMovementReason is the reason of a StockMovement.
type StockMovementReason string

// Allowed StockMovementReason values.
const (
	StockMovementReasonReceive  StockMovementReason = "receive"
	StockMovementReasonIssue    StockMovementReason = "issue"
	StockMovementReasonTransfer StockMovementReason = "transfer"
	StockMovementReasonAdjust   StockMovementReason = "adjust"
	StockMovementReasonReturn   StockMovementReason = "return"
)

// StockMovementReasonValues lists every allowed StockMovementReason.
var StockMovementReasonValues = []StockMovementReason{StockMovementReasonReceive, StockMovementReasonIssue, StockMovementReasonTransfer, StockMovementReasonAdjust, StockMovementReasonReturn}

// Valid reports whether v is one of the allowed values.
func (v StockMovementReason) Valid() bool {
	for _, allowed := range StockMovementReasonValues {
		if v == allowed {
			return true
		}
	}
	return false
}

// Label is a human-friendly name for v.
func (v StockMovementReason) Label() string {
	text := strings.ReplaceAll(string(v), "_", " ")
	return strings.ToUpper(text[:1]) + text[1:]
}

// ParseStockMovementReason turns text into a StockMovementReason.
func ParseStockMovementReason(text string) (StockMovementReason, error) {
	v := StockMovementReason(strings.ToLower(strings.TrimSpace(text)))
	if !v.Valid() {
		return "", Invalid("reason", "must be one of %s", StockMovementReasonList())
	}
	return v, nil
}

// StockMovementReasonList is every allowed value, comma separated.
func StockMovementReasonList() string {
	parts := make([]string, len(StockMovementReasonValues))
	for i, v := range StockMovementReasonValues {
		parts[i] = string(v)
	}
	return strings.Join(parts, ", ")
}

// PurchaseOrderStatus is the status of a PurchaseOrder.
type PurchaseOrderStatus string

// Allowed PurchaseOrderStatus values.
const (
	PurchaseOrderStatusDraft     PurchaseOrderStatus = "draft"
	PurchaseOrderStatusSent      PurchaseOrderStatus = "sent"
	PurchaseOrderStatusPartial   PurchaseOrderStatus = "partial"
	PurchaseOrderStatusReceived  PurchaseOrderStatus = "received"
	PurchaseOrderStatusCancelled PurchaseOrderStatus = "cancelled"
)

// PurchaseOrderStatusValues lists every allowed PurchaseOrderStatus.
var PurchaseOrderStatusValues = []PurchaseOrderStatus{PurchaseOrderStatusDraft, PurchaseOrderStatusSent, PurchaseOrderStatusPartial, PurchaseOrderStatusReceived, PurchaseOrderStatusCancelled}

// Valid reports whether v is one of the allowed values.
func (v PurchaseOrderStatus) Valid() bool {
	for _, allowed := range PurchaseOrderStatusValues {
		if v == allowed {
			return true
		}
	}
	return false
}

// Label is a human-friendly name for v.
func (v PurchaseOrderStatus) Label() string {
	text := strings.ReplaceAll(string(v), "_", " ")
	return strings.ToUpper(text[:1]) + text[1:]
}

// ParsePurchaseOrderStatus turns text into a PurchaseOrderStatus.
func ParsePurchaseOrderStatus(text string) (PurchaseOrderStatus, error) {
	v := PurchaseOrderStatus(strings.ToLower(strings.TrimSpace(text)))
	if !v.Valid() {
		return "", Invalid("status", "must be one of %s", PurchaseOrderStatusList())
	}
	return v, nil
}

// PurchaseOrderStatusList is every allowed value, comma separated.
func PurchaseOrderStatusList() string {
	parts := make([]string, len(PurchaseOrderStatusValues))
	for i, v := range PurchaseOrderStatusValues {
		parts[i] = string(v)
	}
	return strings.Join(parts, ", ")
}

// NotificationChannel is the channel of a Notification.
type NotificationChannel string

// Allowed NotificationChannel values.
const (
	NotificationChannelEmail NotificationChannel = "email"
	NotificationChannelSms   NotificationChannel = "sms"
	NotificationChannelPush  NotificationChannel = "push"
)

// NotificationChannelValues lists every allowed NotificationChannel.
var NotificationChannelValues = []NotificationChannel{NotificationChannelEmail, NotificationChannelSms, NotificationChannelPush}

// Valid reports whether v is one of the allowed values.
func (v NotificationChannel) Valid() bool {
	for _, allowed := range NotificationChannelValues {
		if v == allowed {
			return true
		}
	}
	return false
}

// Label is a human-friendly name for v.
func (v NotificationChannel) Label() string {
	text := strings.ReplaceAll(string(v), "_", " ")
	return strings.ToUpper(text[:1]) + text[1:]
}

// ParseNotificationChannel turns text into a NotificationChannel.
func ParseNotificationChannel(text string) (NotificationChannel, error) {
	v := NotificationChannel(strings.ToLower(strings.TrimSpace(text)))
	if !v.Valid() {
		return "", Invalid("channel", "must be one of %s", NotificationChannelList())
	}
	return v, nil
}

// NotificationChannelList is every allowed value, comma separated.
func NotificationChannelList() string {
	parts := make([]string, len(NotificationChannelValues))
	for i, v := range NotificationChannelValues {
		parts[i] = string(v)
	}
	return strings.Join(parts, ", ")
}

// Supplier is a supplier record.
type Supplier struct {
	ID        int    `json:"id"`
	Name      string `json:"name"`
	Email     string `json:"email"`
	Phone     string `json:"phone"`
	Country   string `json:"country"`
	LeadDays  int    `json:"lead_days"`
	Preferred bool   `json:"preferred"`
}

// Validate checks every field and normalises text and amounts in place.
func (s *Supplier) Validate() error {
	var err error
	if s.Name, err = CheckText("name", s.Name, 120, true); err != nil {
		return err
	}
	if s.Email, err = CheckEmail("email", s.Email); err != nil {
		return err
	}
	if s.Phone, err = CheckText("phone", s.Phone, 120, true); err != nil {
		return err
	}
	if s.Country, err = CheckText("country", s.Country, 120, true); err != nil {
		return err
	}
	if err = CheckInt("lead_days", s.LeadDays); err != nil {
		return err
	}
	return nil
}

// Summary is one line for logs and lists.
func (s Supplier) Summary() string {
	return fmt.Sprintf("Supplier #%d: %s", s.ID, s.Name)
}

// Map is the record as plain values (for CSV export and templates).
func (s Supplier) Map() map[string]any {
	return map[string]any{
		"id":        s.ID,
		"name":      s.Name,
		"email":     s.Email,
		"phone":     s.Phone,
		"country":   s.Country,
		"lead_days": s.LeadDays,
		"preferred": s.Preferred,
	}
}

// CompareSupplierByName orders suppliers by name (for slices.SortFunc).
func CompareSupplierByName(a, b Supplier) int {
	return cmp.Compare(a.Name, b.Name)
}

// CompareSupplierByEmail orders suppliers by email (for slices.SortFunc).
func CompareSupplierByEmail(a, b Supplier) int {
	return cmp.Compare(a.Email, b.Email)
}

// CompareSupplierByPhone orders suppliers by phone (for slices.SortFunc).
func CompareSupplierByPhone(a, b Supplier) int {
	return cmp.Compare(a.Phone, b.Phone)
}

// CompareSupplierByCountry orders suppliers by country (for slices.SortFunc).
func CompareSupplierByCountry(a, b Supplier) int {
	return cmp.Compare(a.Country, b.Country)
}

// CompareSupplierByLeadDays orders suppliers by lead days (for slices.SortFunc).
func CompareSupplierByLeadDays(a, b Supplier) int {
	return cmp.Compare(a.LeadDays, b.LeadDays)
}

// SupplierPatch changes some fields of a Supplier; nil means "leave as it is".
type SupplierPatch struct {
	Name      *string `json:"name,omitempty"`
	Email     *string `json:"email,omitempty"`
	Phone     *string `json:"phone,omitempty"`
	Country   *string `json:"country,omitempty"`
	LeadDays  *int    `json:"lead_days,omitempty"`
	Preferred *bool   `json:"preferred,omitempty"`
}

// Apply returns a validated copy of item with the patch applied.
func (p SupplierPatch) Apply(item Supplier) (Supplier, error) {
	if p.Name != nil {
		item.Name = *p.Name
	}
	if p.Email != nil {
		item.Email = *p.Email
	}
	if p.Phone != nil {
		item.Phone = *p.Phone
	}
	if p.Country != nil {
		item.Country = *p.Country
	}
	if p.LeadDays != nil {
		item.LeadDays = *p.LeadDays
	}
	if p.Preferred != nil {
		item.Preferred = *p.Preferred
	}
	err := item.Validate()
	return item, err
}

// Product is a product record.
type Product struct {
	ID           int             `json:"id"`
	SupplierID   int             `json:"supplier_id"`
	Sku          string          `json:"sku"`
	Name         string          `json:"name"`
	UnitCost     float64         `json:"unit_cost"`
	UnitPrice    float64         `json:"unit_price"`
	ReorderLevel int             `json:"reorder_level"`
	Category     ProductCategory `json:"category"`
	Active       bool            `json:"active"`
}

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

// Map is the record as plain values (for CSV export and templates).
func (p Product) Map() map[string]any {
	return map[string]any{
		"id":            p.ID,
		"supplier_id":   p.SupplierID,
		"sku":           p.Sku,
		"name":          p.Name,
		"unit_cost":     p.UnitCost,
		"unit_price":    p.UnitPrice,
		"reorder_level": p.ReorderLevel,
		"category":      string(p.Category),
		"active":        p.Active,
	}
}

// CompareProductBySupplierID orders products by supplier id (for slices.SortFunc).
func CompareProductBySupplierID(a, b Product) int {
	return cmp.Compare(a.SupplierID, b.SupplierID)
}

// CompareProductBySku orders products by sku (for slices.SortFunc).
func CompareProductBySku(a, b Product) int {
	return cmp.Compare(a.Sku, b.Sku)
}

// CompareProductByName orders products by name (for slices.SortFunc).
func CompareProductByName(a, b Product) int {
	return cmp.Compare(a.Name, b.Name)
}

// CompareProductByUnitCost orders products by unit cost (for slices.SortFunc).
func CompareProductByUnitCost(a, b Product) int {
	return cmp.Compare(a.UnitCost, b.UnitCost)
}

// CompareProductByUnitPrice orders products by unit price (for slices.SortFunc).
func CompareProductByUnitPrice(a, b Product) int {
	return cmp.Compare(a.UnitPrice, b.UnitPrice)
}

// CompareProductByReorderLevel orders products by reorder level (for slices.SortFunc).
func CompareProductByReorderLevel(a, b Product) int {
	return cmp.Compare(a.ReorderLevel, b.ReorderLevel)
}

// CompareProductByCategory orders products by category (for slices.SortFunc).
func CompareProductByCategory(a, b Product) int {
	return cmp.Compare(string(a.Category), string(b.Category))
}

// ProductPatch changes some fields of a Product; nil means "leave as it is".
type ProductPatch struct {
	SupplierID   *int             `json:"supplier_id,omitempty"`
	Sku          *string          `json:"sku,omitempty"`
	Name         *string          `json:"name,omitempty"`
	UnitCost     *float64         `json:"unit_cost,omitempty"`
	UnitPrice    *float64         `json:"unit_price,omitempty"`
	ReorderLevel *int             `json:"reorder_level,omitempty"`
	Category     *ProductCategory `json:"category,omitempty"`
	Active       *bool            `json:"active,omitempty"`
}

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

// Map is the record as plain values (for CSV export and templates).
func (b Bin) Map() map[string]any {
	return map[string]any{
		"id":           b.ID,
		"code":         b.Code,
		"aisle":        b.Aisle,
		"shelf":        b.Shelf,
		"capacity":     b.Capacity,
		"refrigerated": b.Refrigerated,
	}
}

// CompareBinByCode orders bins by code (for slices.SortFunc).
func CompareBinByCode(a, b Bin) int {
	return cmp.Compare(a.Code, b.Code)
}

// CompareBinByAisle orders bins by aisle (for slices.SortFunc).
func CompareBinByAisle(a, b Bin) int {
	return cmp.Compare(a.Aisle, b.Aisle)
}

// CompareBinByShelf orders bins by shelf (for slices.SortFunc).
func CompareBinByShelf(a, b Bin) int {
	return cmp.Compare(a.Shelf, b.Shelf)
}

// CompareBinByCapacity orders bins by capacity (for slices.SortFunc).
func CompareBinByCapacity(a, b Bin) int {
	return cmp.Compare(a.Capacity, b.Capacity)
}

// BinPatch changes some fields of a Bin; nil means "leave as it is".
type BinPatch struct {
	Code         *string `json:"code,omitempty"`
	Aisle        *string `json:"aisle,omitempty"`
	Shelf        *int    `json:"shelf,omitempty"`
	Capacity     *int    `json:"capacity,omitempty"`
	Refrigerated *bool   `json:"refrigerated,omitempty"`
}

// Apply returns a validated copy of item with the patch applied.
func (p BinPatch) Apply(item Bin) (Bin, error) {
	if p.Code != nil {
		item.Code = *p.Code
	}
	if p.Aisle != nil {
		item.Aisle = *p.Aisle
	}
	if p.Shelf != nil {
		item.Shelf = *p.Shelf
	}
	if p.Capacity != nil {
		item.Capacity = *p.Capacity
	}
	if p.Refrigerated != nil {
		item.Refrigerated = *p.Refrigerated
	}
	err := item.Validate()
	return item, err
}

// StockMovement is a stock movement record.
type StockMovement struct {
	ID        int                 `json:"id"`
	ProductID int                 `json:"product_id"`
	BinID     int                 `json:"bin_id"`
	Quantity  int                 `json:"quantity"`
	Moved     string              `json:"moved"`
	Reason    StockMovementReason `json:"reason"`
	Reference string              `json:"reference"`
}

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

// CompareStockMovementByReference orders stock movements by reference (for slices.SortFunc).
func CompareStockMovementByReference(a, b StockMovement) int {
	return cmp.Compare(a.Reference, b.Reference)
}

// StockMovementPatch changes some fields of a StockMovement; nil means "leave as it is".
type StockMovementPatch struct {
	ProductID *int                 `json:"product_id,omitempty"`
	BinID     *int                 `json:"bin_id,omitempty"`
	Quantity  *int                 `json:"quantity,omitempty"`
	Moved     *string              `json:"moved,omitempty"`
	Reason    *StockMovementReason `json:"reason,omitempty"`
	Reference *string              `json:"reference,omitempty"`
}

// Apply returns a validated copy of item with the patch applied.
func (p StockMovementPatch) Apply(item StockMovement) (StockMovement, error) {
	if p.ProductID != nil {
		item.ProductID = *p.ProductID
	}
	if p.BinID != nil {
		item.BinID = *p.BinID
	}
	if p.Quantity != nil {
		item.Quantity = *p.Quantity
	}
	if p.Moved != nil {
		item.Moved = *p.Moved
	}
	if p.Reason != nil {
		item.Reason = *p.Reason
	}
	if p.Reference != nil {
		item.Reference = *p.Reference
	}
	err := item.Validate()
	return item, err
}

// PurchaseOrder is a purchase order record.
type PurchaseOrder struct {
	ID         int                 `json:"id"`
	SupplierID int                 `json:"supplier_id"`
	Ordered    string              `json:"ordered"`
	Expected   string              `json:"expected"`
	Total      float64             `json:"total"`
	Status     PurchaseOrderStatus `json:"status"`
	Notes      string              `json:"notes"`
}

// Validate checks every field and normalises text and amounts in place.
func (p *PurchaseOrder) Validate() error {
	var err error
	if err = CheckRef("supplier_id", p.SupplierID); err != nil {
		return err
	}
	if err = CheckDate("ordered", p.Ordered); err != nil {
		return err
	}
	if err = CheckDate("expected", p.Expected); err != nil {
		return err
	}
	if err = CheckNumber("total", p.Total); err != nil {
		return err
	}
	p.Total = math.Round(p.Total*100) / 100
	if !p.Status.Valid() {
		return Invalid("status", "must be one of %s", PurchaseOrderStatusList())
	}
	if p.Notes, err = CheckText("notes", p.Notes, 2000, false); err != nil {
		return err
	}
	return nil
}

// Summary is one line for logs and lists.
func (p PurchaseOrder) Summary() string {
	return fmt.Sprintf("PurchaseOrder #%d", p.ID)
}

// Map is the record as plain values (for CSV export and templates).
func (p PurchaseOrder) Map() map[string]any {
	return map[string]any{
		"id":          p.ID,
		"supplier_id": p.SupplierID,
		"ordered":     p.Ordered,
		"expected":    p.Expected,
		"total":       p.Total,
		"status":      string(p.Status),
		"notes":       p.Notes,
	}
}

// ComparePurchaseOrderBySupplierID orders purchase orders by supplier id (for slices.SortFunc).
func ComparePurchaseOrderBySupplierID(a, b PurchaseOrder) int {
	return cmp.Compare(a.SupplierID, b.SupplierID)
}

// ComparePurchaseOrderByOrdered orders purchase orders by ordered (for slices.SortFunc).
func ComparePurchaseOrderByOrdered(a, b PurchaseOrder) int {
	return cmp.Compare(a.Ordered, b.Ordered)
}

// ComparePurchaseOrderByExpected orders purchase orders by expected (for slices.SortFunc).
func ComparePurchaseOrderByExpected(a, b PurchaseOrder) int {
	return cmp.Compare(a.Expected, b.Expected)
}

// ComparePurchaseOrderByTotal orders purchase orders by total (for slices.SortFunc).
func ComparePurchaseOrderByTotal(a, b PurchaseOrder) int {
	return cmp.Compare(a.Total, b.Total)
}

// ComparePurchaseOrderByStatus orders purchase orders by status (for slices.SortFunc).
func ComparePurchaseOrderByStatus(a, b PurchaseOrder) int {
	return cmp.Compare(string(a.Status), string(b.Status))
}

// ComparePurchaseOrderByNotes orders purchase orders by notes (for slices.SortFunc).
func ComparePurchaseOrderByNotes(a, b PurchaseOrder) int {
	return cmp.Compare(a.Notes, b.Notes)
}

// PurchaseOrderPatch changes some fields of a PurchaseOrder; nil means "leave as it is".
type PurchaseOrderPatch struct {
	SupplierID *int                 `json:"supplier_id,omitempty"`
	Ordered    *string              `json:"ordered,omitempty"`
	Expected   *string              `json:"expected,omitempty"`
	Total      *float64             `json:"total,omitempty"`
	Status     *PurchaseOrderStatus `json:"status,omitempty"`
	Notes      *string              `json:"notes,omitempty"`
}

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

// Document is a document record.
type Document struct {
	ID         int    `json:"id"`
	SupplierID int    `json:"supplier_id"`
	Title      string `json:"title"`
	Pages      int    `json:"pages"`
	Signed     bool   `json:"signed"`
	Version    int    `json:"version"`
	Issued     string `json:"issued"`
}

// Validate checks every field and normalises text and amounts in place.
func (d *Document) Validate() error {
	var err error
	if err = CheckRef("supplier_id", d.SupplierID); err != nil {
		return err
	}
	if d.Title, err = CheckText("title", d.Title, 120, true); err != nil {
		return err
	}
	if err = CheckInt("pages", d.Pages); err != nil {
		return err
	}
	if err = CheckInt("version", d.Version); err != nil {
		return err
	}
	if err = CheckDate("issued", d.Issued); err != nil {
		return err
	}
	return nil
}

// Summary is one line for logs and lists.
func (d Document) Summary() string {
	return fmt.Sprintf("Document #%d: %s", d.ID, d.Title)
}

// Map is the record as plain values (for CSV export and templates).
func (d Document) Map() map[string]any {
	return map[string]any{
		"id":          d.ID,
		"supplier_id": d.SupplierID,
		"title":       d.Title,
		"pages":       d.Pages,
		"signed":      d.Signed,
		"version":     d.Version,
		"issued":      d.Issued,
	}
}

// CompareDocumentBySupplierID orders documents by supplier id (for slices.SortFunc).
func CompareDocumentBySupplierID(a, b Document) int {
	return cmp.Compare(a.SupplierID, b.SupplierID)
}

// CompareDocumentByTitle orders documents by title (for slices.SortFunc).
func CompareDocumentByTitle(a, b Document) int {
	return cmp.Compare(a.Title, b.Title)
}

// CompareDocumentByPages orders documents by pages (for slices.SortFunc).
func CompareDocumentByPages(a, b Document) int {
	return cmp.Compare(a.Pages, b.Pages)
}

// CompareDocumentByVersion orders documents by version (for slices.SortFunc).
func CompareDocumentByVersion(a, b Document) int {
	return cmp.Compare(a.Version, b.Version)
}

// CompareDocumentByIssued orders documents by issued (for slices.SortFunc).
func CompareDocumentByIssued(a, b Document) int {
	return cmp.Compare(a.Issued, b.Issued)
}

// DocumentPatch changes some fields of a Document; nil means "leave as it is".
type DocumentPatch struct {
	SupplierID *int    `json:"supplier_id,omitempty"`
	Title      *string `json:"title,omitempty"`
	Pages      *int    `json:"pages,omitempty"`
	Signed     *bool   `json:"signed,omitempty"`
	Version    *int    `json:"version,omitempty"`
	Issued     *string `json:"issued,omitempty"`
}

// Apply returns a validated copy of item with the patch applied.
func (p DocumentPatch) Apply(item Document) (Document, error) {
	if p.SupplierID != nil {
		item.SupplierID = *p.SupplierID
	}
	if p.Title != nil {
		item.Title = *p.Title
	}
	if p.Pages != nil {
		item.Pages = *p.Pages
	}
	if p.Signed != nil {
		item.Signed = *p.Signed
	}
	if p.Version != nil {
		item.Version = *p.Version
	}
	if p.Issued != nil {
		item.Issued = *p.Issued
	}
	err := item.Validate()
	return item, err
}

// Notification is a notification record.
type Notification struct {
	ID        int                 `json:"id"`
	Recipient string              `json:"recipient"`
	Title     string              `json:"title"`
	Sent      string              `json:"sent"`
	Channel   NotificationChannel `json:"channel"`
	Read      bool                `json:"read"`
}

// Validate checks every field and normalises text and amounts in place.
func (n *Notification) Validate() error {
	var err error
	if n.Recipient, err = CheckEmail("recipient", n.Recipient); err != nil {
		return err
	}
	if n.Title, err = CheckText("title", n.Title, 120, true); err != nil {
		return err
	}
	if err = CheckDate("sent", n.Sent); err != nil {
		return err
	}
	if !n.Channel.Valid() {
		return Invalid("channel", "must be one of %s", NotificationChannelList())
	}
	return nil
}

// Summary is one line for logs and lists.
func (n Notification) Summary() string {
	return fmt.Sprintf("Notification #%d: %s", n.ID, n.Recipient)
}

// Map is the record as plain values (for CSV export and templates).
func (n Notification) Map() map[string]any {
	return map[string]any{
		"id":        n.ID,
		"recipient": n.Recipient,
		"title":     n.Title,
		"sent":      n.Sent,
		"channel":   string(n.Channel),
		"read":      n.Read,
	}
}

// CompareNotificationByRecipient orders notifications by recipient (for slices.SortFunc).
func CompareNotificationByRecipient(a, b Notification) int {
	return cmp.Compare(a.Recipient, b.Recipient)
}

// CompareNotificationByTitle orders notifications by title (for slices.SortFunc).
func CompareNotificationByTitle(a, b Notification) int {
	return cmp.Compare(a.Title, b.Title)
}

// CompareNotificationBySent orders notifications by sent (for slices.SortFunc).
func CompareNotificationBySent(a, b Notification) int {
	return cmp.Compare(a.Sent, b.Sent)
}

// CompareNotificationByChannel orders notifications by channel (for slices.SortFunc).
func CompareNotificationByChannel(a, b Notification) int {
	return cmp.Compare(string(a.Channel), string(b.Channel))
}

// NotificationPatch changes some fields of a Notification; nil means "leave as it is".
type NotificationPatch struct {
	Recipient *string              `json:"recipient,omitempty"`
	Title     *string              `json:"title,omitempty"`
	Sent      *string              `json:"sent,omitempty"`
	Channel   *NotificationChannel `json:"channel,omitempty"`
	Read      *bool                `json:"read,omitempty"`
}

// Apply returns a validated copy of item with the patch applied.
func (p NotificationPatch) Apply(item Notification) (Notification, error) {
	if p.Recipient != nil {
		item.Recipient = *p.Recipient
	}
	if p.Title != nil {
		item.Title = *p.Title
	}
	if p.Sent != nil {
		item.Sent = *p.Sent
	}
	if p.Channel != nil {
		item.Channel = *p.Channel
	}
	if p.Read != nil {
		item.Read = *p.Read
	}
	err := item.Validate()
	return item, err
}
