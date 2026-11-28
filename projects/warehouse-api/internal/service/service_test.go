package service_test

import (
	"bytes"
	"encoding/json"
	"errors"
	"fmt"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"

	"warehouse-api/internal/httpapi"
	"warehouse-api/internal/model"
	"warehouse-api/internal/service"
)

func seeded(t *testing.T) *service.Service {
	t.Helper()
	svc := service.New()
	if err := svc.Seed(3); err != nil {
		t.Fatalf("seed: %v", err)
	}
	return svc
}

func wantField(t *testing.T, err error, field string) {
	t.Helper()
	var invalid *model.ValidationError
	if !errors.As(err, &invalid) || invalid.Field != field {
		t.Fatalf("want a validation error on %q, got %v", field, err)
	}
}

func call(t *testing.T, h http.Handler, method, path string, body any) *httptest.ResponseRecorder {
	t.Helper()
	var reader *bytes.Reader
	if body == nil {
		reader = bytes.NewReader(nil)
	} else {
		data, err := json.Marshal(body)
		if err != nil {
			t.Fatalf("marshal: %v", err)
		}
		reader = bytes.NewReader(data)
	}
	rec := httptest.NewRecorder()
	h.ServeHTTP(rec, httptest.NewRequest(method, path, reader))
	return rec
}

// keep the imports used even for domains without text fields
var _ = strings.ToUpper

func TestSupplierCreateAndGet(t *testing.T) {
	svc := seeded(t)
	created, err := svc.CreateSupplier(service.SampleSupplier(10))
	if err != nil {
		t.Fatalf("create: %v", err)
	}
	got, err := svc.GetSupplier(created.ID)
	if err != nil || got != created {
		t.Fatalf("get = %+v, %v; want %+v", got, err, created)
	}
	if n := len(svc.ListSuppliers()); n != 4 {
		t.Fatalf("list has %d records, want 4", n)
	}
}

func TestSupplierMissing(t *testing.T) {
	svc := seeded(t)
	if _, err := svc.GetSupplier(9999); !errors.Is(err, service.ErrNotFound) {
		t.Fatalf("want ErrNotFound, got %v", err)
	}
}

func TestSupplierRejectsBadName(t *testing.T) {
	svc := seeded(t)
	item := service.SampleSupplier(12)
	item.Name = ""
	_, err := svc.CreateSupplier(item)
	wantField(t, err, "name")
}

func TestSupplierRejectsBadEmail(t *testing.T) {
	svc := seeded(t)
	item := service.SampleSupplier(12)
	item.Email = "not-an-email"
	_, err := svc.CreateSupplier(item)
	wantField(t, err, "email")
}

func TestSupplierRejectsBadPhone(t *testing.T) {
	svc := seeded(t)
	item := service.SampleSupplier(12)
	item.Phone = ""
	_, err := svc.CreateSupplier(item)
	wantField(t, err, "phone")
}

func TestSupplierRejectsBadCountry(t *testing.T) {
	svc := seeded(t)
	item := service.SampleSupplier(12)
	item.Country = ""
	_, err := svc.CreateSupplier(item)
	wantField(t, err, "country")
}

func TestSupplierRejectsBadLeadDays(t *testing.T) {
	svc := seeded(t)
	item := service.SampleSupplier(12)
	item.LeadDays = -1
	_, err := svc.CreateSupplier(item)
	wantField(t, err, "lead_days")
}

func TestSearchSupplierName(t *testing.T) {
	svc := seeded(t)
	target, _ := svc.GetSupplier(2)
	for _, item := range svc.Suppliers.SearchName(strings.ToUpper(target.Name)) {
		if item.ID == target.ID {
			return
		}
	}
	t.Fatalf("search did not find %q", target.Name)
}

func TestSearchSupplierEmail(t *testing.T) {
	svc := seeded(t)
	target, _ := svc.GetSupplier(2)
	for _, item := range svc.Suppliers.SearchEmail(strings.ToUpper(target.Email)) {
		if item.ID == target.ID {
			return
		}
	}
	t.Fatalf("search did not find %q", target.Email)
}

func TestSearchSupplierPhone(t *testing.T) {
	svc := seeded(t)
	target, _ := svc.GetSupplier(2)
	for _, item := range svc.Suppliers.SearchPhone(strings.ToUpper(target.Phone)) {
		if item.ID == target.ID {
			return
		}
	}
	t.Fatalf("search did not find %q", target.Phone)
}

func TestSearchSupplierCountry(t *testing.T) {
	svc := seeded(t)
	target, _ := svc.GetSupplier(2)
	for _, item := range svc.Suppliers.SearchCountry(strings.ToUpper(target.Country)) {
		if item.ID == target.ID {
			return
		}
	}
	t.Fatalf("search did not find %q", target.Country)
}

func TestAdjustSupplierLeadDays(t *testing.T) {
	svc := seeded(t)
	before, _ := svc.GetSupplier(1)
	after, err := svc.AdjustSupplierLeadDays(1, 2)
	if err != nil || after.LeadDays != before.LeadDays+2 {
		t.Fatalf("adjust = %v, %v", after.LeadDays, err)
	}
	_, err = svc.AdjustSupplierLeadDays(1, -(after.LeadDays + 100))
	wantField(t, err, "lead_days")
}

func TestToggleSupplierPreferred(t *testing.T) {
	svc := seeded(t)
	before, _ := svc.GetSupplier(1)
	after, err := svc.ToggleSupplierPreferred(1)
	if err != nil || after.Preferred == before.Preferred {
		t.Fatalf("toggle = %v, %v", after.Preferred, err)
	}
}

func TestDeleteSupplier(t *testing.T) {
	svc := seeded(t)
	item, err := svc.CreateSupplier(service.SampleSupplier(14))
	if err != nil {
		t.Fatalf("create: %v", err)
	}
	if err := svc.DeleteSupplier(item.ID); err != nil {
		t.Fatalf("delete: %v", err)
	}
	if _, err := svc.GetSupplier(item.ID); !errors.Is(err, service.ErrNotFound) {
		t.Fatalf("still there: %v", err)
	}
}

func TestDeleteSupplierInUse(t *testing.T) {
	svc := seeded(t)
	if err := svc.DeleteSupplier(1); !errors.Is(err, service.ErrConflict) {
		t.Fatalf("want ErrConflict, got %v", err)
	}
}

func TestSupplierStats(t *testing.T) {
	svc := seeded(t)
	if got := svc.SupplierStats().Count; got != 3 {
		t.Fatalf("count = %d", got)
	}
}

func TestSupplierAPI(t *testing.T) {
	h := httpapi.New(seeded(t))
	rec := call(t, h, http.MethodPost, "/suppliers", service.SampleSupplier(15))
	if rec.Code != http.StatusCreated {
		t.Fatalf("POST = %d %s", rec.Code, rec.Body)
	}
	var created model.Supplier
	if err := json.Unmarshal(rec.Body.Bytes(), &created); err != nil {
		t.Fatalf("decode: %v", err)
	}
	path := fmt.Sprintf("/suppliers/%d", created.ID)
	if rec := call(t, h, http.MethodGet, path, nil); rec.Code != http.StatusOK {
		t.Fatalf("GET = %d", rec.Code)
	}
	if rec := call(t, h, http.MethodGet, "/suppliers?size=2&page=1", nil); rec.Code != http.StatusOK {
		t.Fatalf("list = %d", rec.Code)
	}
	if rec := call(t, h, http.MethodGet, "/suppliers/stats", nil); rec.Code != http.StatusOK {
		t.Fatalf("stats = %d", rec.Code)
	}
	if rec := call(t, h, http.MethodPost, "/suppliers", map[string]int{"no_such_field": 1}); rec.Code != http.StatusBadRequest {
		t.Fatalf("bad POST = %d", rec.Code)
	}
	if rec := call(t, h, http.MethodDelete, path, nil); rec.Code != http.StatusNoContent {
		t.Fatalf("DELETE = %d", rec.Code)
	}
	if rec := call(t, h, http.MethodGet, path, nil); rec.Code != http.StatusNotFound {
		t.Fatalf("GET after delete = %d", rec.Code)
	}
}

func TestProductCreateAndGet(t *testing.T) {
	svc := seeded(t)
	created, err := svc.CreateProduct(service.SampleProduct(10))
	if err != nil {
		t.Fatalf("create: %v", err)
	}
	got, err := svc.GetProduct(created.ID)
	if err != nil || got != created {
		t.Fatalf("get = %+v, %v; want %+v", got, err, created)
	}
	if n := len(svc.ListProducts()); n != 4 {
		t.Fatalf("list has %d records, want 4", n)
	}
}

func TestProductMissing(t *testing.T) {
	svc := seeded(t)
	if _, err := svc.GetProduct(9999); !errors.Is(err, service.ErrNotFound) {
		t.Fatalf("want ErrNotFound, got %v", err)
	}
}

func TestProductRejectsBadSupplierID(t *testing.T) {
	svc := seeded(t)
	item := service.SampleProduct(12)
	item.SupplierID = 0
	_, err := svc.CreateProduct(item)
	wantField(t, err, "supplier_id")
}

func TestProductRejectsBadSku(t *testing.T) {
	svc := seeded(t)
	item := service.SampleProduct(12)
	item.Sku = ""
	_, err := svc.CreateProduct(item)
	wantField(t, err, "sku")
}

func TestProductRejectsBadName(t *testing.T) {
	svc := seeded(t)
	item := service.SampleProduct(12)
	item.Name = ""
	_, err := svc.CreateProduct(item)
	wantField(t, err, "name")
}

func TestProductRejectsBadUnitCost(t *testing.T) {
	svc := seeded(t)
	item := service.SampleProduct(12)
	item.UnitCost = -5
	_, err := svc.CreateProduct(item)
	wantField(t, err, "unit_cost")
}

func TestProductRejectsBadUnitPrice(t *testing.T) {
	svc := seeded(t)
	item := service.SampleProduct(12)
	item.UnitPrice = -5
	_, err := svc.CreateProduct(item)
	wantField(t, err, "unit_price")
}

func TestProductRejectsBadReorderLevel(t *testing.T) {
	svc := seeded(t)
	item := service.SampleProduct(12)
	item.ReorderLevel = -1
	_, err := svc.CreateProduct(item)
	wantField(t, err, "reorder_level")
}

func TestProductRejectsBadCategory(t *testing.T) {
	svc := seeded(t)
	item := service.SampleProduct(12)
	item.Category = "nope"
	_, err := svc.CreateProduct(item)
	wantField(t, err, "category")
}

func TestProductSupplierIDMustExist(t *testing.T) {
	svc := seeded(t)
	item := service.SampleProduct(13)
	item.SupplierID = 9999
	if _, err := svc.CreateProduct(item); !errors.Is(err, service.ErrNotFound) {
		t.Fatalf("want ErrNotFound, got %v", err)
	}
}

func TestSearchProductSku(t *testing.T) {
	svc := seeded(t)
	target, _ := svc.GetProduct(2)
	for _, item := range svc.Products.SearchSku(strings.ToUpper(target.Sku)) {
		if item.ID == target.ID {
			return
		}
	}
	t.Fatalf("search did not find %q", target.Sku)
}

func TestSearchProductName(t *testing.T) {
	svc := seeded(t)
	target, _ := svc.GetProduct(2)
	for _, item := range svc.Products.SearchName(strings.ToUpper(target.Name)) {
		if item.ID == target.ID {
			return
		}
	}
	t.Fatalf("search did not find %q", target.Name)
}

func TestAdjustProductUnitCost(t *testing.T) {
	svc := seeded(t)
	before, _ := svc.GetProduct(1)
	after, err := svc.AdjustProductUnitCost(1, 1.5)
	if err != nil || after.UnitCost-before.UnitCost < 1.49 || after.UnitCost-before.UnitCost > 1.51 {
		t.Fatalf("adjust = %v, %v", after.UnitCost, err)
	}
}

func TestAdjustProductUnitPrice(t *testing.T) {
	svc := seeded(t)
	before, _ := svc.GetProduct(1)
	after, err := svc.AdjustProductUnitPrice(1, 1.5)
	if err != nil || after.UnitPrice-before.UnitPrice < 1.49 || after.UnitPrice-before.UnitPrice > 1.51 {
		t.Fatalf("adjust = %v, %v", after.UnitPrice, err)
	}
}

func TestAdjustProductReorderLevel(t *testing.T) {
	svc := seeded(t)
	before, _ := svc.GetProduct(1)
	after, err := svc.AdjustProductReorderLevel(1, 2)
	if err != nil || after.ReorderLevel != before.ReorderLevel+2 {
		t.Fatalf("adjust = %v, %v", after.ReorderLevel, err)
	}
	_, err = svc.AdjustProductReorderLevel(1, -(after.ReorderLevel + 100))
	wantField(t, err, "reorder_level")
}

func TestSetProductCategory(t *testing.T) {
	svc := seeded(t)
	last := model.ProductCategoryValues[len(model.ProductCategoryValues)-1]
	item, err := svc.SetProductCategory(1, last)
	if err != nil || item.Category != last {
		t.Fatalf("set = %v, %v", item.Category, err)
	}
	if got, want := svc.Products.CountByCategory()[last], len(svc.Products.WithCategory(last)); got != want {
		t.Fatalf("count %d != %d", got, want)
	}
}

func TestToggleProductActive(t *testing.T) {
	svc := seeded(t)
	before, _ := svc.GetProduct(1)
	after, err := svc.ToggleProductActive(1)
	if err != nil || after.Active == before.Active {
		t.Fatalf("toggle = %v, %v", after.Active, err)
	}
}

func TestDeleteProduct(t *testing.T) {
	svc := seeded(t)
	item, err := svc.CreateProduct(service.SampleProduct(14))
	if err != nil {
		t.Fatalf("create: %v", err)
	}
	if err := svc.DeleteProduct(item.ID); err != nil {
		t.Fatalf("delete: %v", err)
	}
	if _, err := svc.GetProduct(item.ID); !errors.Is(err, service.ErrNotFound) {
		t.Fatalf("still there: %v", err)
	}
}

func TestDeleteProductInUse(t *testing.T) {
	svc := seeded(t)
	if err := svc.DeleteProduct(1); !errors.Is(err, service.ErrConflict) {
		t.Fatalf("want ErrConflict, got %v", err)
	}
}

func TestProductStats(t *testing.T) {
	svc := seeded(t)
	if got := svc.ProductStats().Count; got != 3 {
		t.Fatalf("count = %d", got)
	}
}

func TestProductAPI(t *testing.T) {
	h := httpapi.New(seeded(t))
	rec := call(t, h, http.MethodPost, "/products", service.SampleProduct(15))
	if rec.Code != http.StatusCreated {
		t.Fatalf("POST = %d %s", rec.Code, rec.Body)
	}
	var created model.Product
	if err := json.Unmarshal(rec.Body.Bytes(), &created); err != nil {
		t.Fatalf("decode: %v", err)
	}
	path := fmt.Sprintf("/products/%d", created.ID)
	if rec := call(t, h, http.MethodGet, path, nil); rec.Code != http.StatusOK {
		t.Fatalf("GET = %d", rec.Code)
	}
	if rec := call(t, h, http.MethodGet, "/products?size=2&page=1", nil); rec.Code != http.StatusOK {
		t.Fatalf("list = %d", rec.Code)
	}
	if rec := call(t, h, http.MethodGet, "/products/stats", nil); rec.Code != http.StatusOK {
		t.Fatalf("stats = %d", rec.Code)
	}
	if rec := call(t, h, http.MethodPost, "/products", map[string]int{"no_such_field": 1}); rec.Code != http.StatusBadRequest {
		t.Fatalf("bad POST = %d", rec.Code)
	}
	if rec := call(t, h, http.MethodDelete, path, nil); rec.Code != http.StatusNoContent {
		t.Fatalf("DELETE = %d", rec.Code)
	}
	if rec := call(t, h, http.MethodGet, path, nil); rec.Code != http.StatusNotFound {
		t.Fatalf("GET after delete = %d", rec.Code)
	}
}

func TestBinCreateAndGet(t *testing.T) {
	svc := seeded(t)
	created, err := svc.CreateBin(service.SampleBin(10))
	if err != nil {
		t.Fatalf("create: %v", err)
	}
	got, err := svc.GetBin(created.ID)
	if err != nil || got != created {
		t.Fatalf("get = %+v, %v; want %+v", got, err, created)
	}
	if n := len(svc.ListBins()); n != 4 {
		t.Fatalf("list has %d records, want 4", n)
	}
}

func TestBinMissing(t *testing.T) {
	svc := seeded(t)
	if _, err := svc.GetBin(9999); !errors.Is(err, service.ErrNotFound) {
		t.Fatalf("want ErrNotFound, got %v", err)
	}
}

func TestBinRejectsBadCode(t *testing.T) {
	svc := seeded(t)
	item := service.SampleBin(12)
	item.Code = ""
	_, err := svc.CreateBin(item)
	wantField(t, err, "code")
}

func TestBinRejectsBadAisle(t *testing.T) {
	svc := seeded(t)
	item := service.SampleBin(12)
	item.Aisle = ""
	_, err := svc.CreateBin(item)
	wantField(t, err, "aisle")
}

func TestBinRejectsBadShelf(t *testing.T) {
	svc := seeded(t)
	item := service.SampleBin(12)
	item.Shelf = -1
	_, err := svc.CreateBin(item)
	wantField(t, err, "shelf")
}

func TestBinRejectsBadCapacity(t *testing.T) {
	svc := seeded(t)
	item := service.SampleBin(12)
	item.Capacity = -1
	_, err := svc.CreateBin(item)
	wantField(t, err, "capacity")
}

func TestSearchBinCode(t *testing.T) {
	svc := seeded(t)
	target, _ := svc.GetBin(2)
	for _, item := range svc.Bins.SearchCode(strings.ToUpper(target.Code)) {
		if item.ID == target.ID {
			return
		}
	}
	t.Fatalf("search did not find %q", target.Code)
}

func TestSearchBinAisle(t *testing.T) {
	svc := seeded(t)
	target, _ := svc.GetBin(2)
	for _, item := range svc.Bins.SearchAisle(strings.ToUpper(target.Aisle)) {
		if item.ID == target.ID {
			return
		}
	}
	t.Fatalf("search did not find %q", target.Aisle)
}

func TestAdjustBinShelf(t *testing.T) {
	svc := seeded(t)
	before, _ := svc.GetBin(1)
	after, err := svc.AdjustBinShelf(1, 2)
	if err != nil || after.Shelf != before.Shelf+2 {
		t.Fatalf("adjust = %v, %v", after.Shelf, err)
	}
	_, err = svc.AdjustBinShelf(1, -(after.Shelf + 100))
	wantField(t, err, "shelf")
}

func TestAdjustBinCapacity(t *testing.T) {
	svc := seeded(t)
	before, _ := svc.GetBin(1)
	after, err := svc.AdjustBinCapacity(1, 2)
	if err != nil || after.Capacity != before.Capacity+2 {
		t.Fatalf("adjust = %v, %v", after.Capacity, err)
	}
	_, err = svc.AdjustBinCapacity(1, -(after.Capacity + 100))
	wantField(t, err, "capacity")
}

func TestToggleBinRefrigerated(t *testing.T) {
	svc := seeded(t)
	before, _ := svc.GetBin(1)
	after, err := svc.ToggleBinRefrigerated(1)
	if err != nil || after.Refrigerated == before.Refrigerated {
		t.Fatalf("toggle = %v, %v", after.Refrigerated, err)
	}
}

func TestDeleteBin(t *testing.T) {
	svc := seeded(t)
	item, err := svc.CreateBin(service.SampleBin(14))
	if err != nil {
		t.Fatalf("create: %v", err)
	}
	if err := svc.DeleteBin(item.ID); err != nil {
		t.Fatalf("delete: %v", err)
	}
	if _, err := svc.GetBin(item.ID); !errors.Is(err, service.ErrNotFound) {
		t.Fatalf("still there: %v", err)
	}
}

func TestDeleteBinInUse(t *testing.T) {
	svc := seeded(t)
	if err := svc.DeleteBin(1); !errors.Is(err, service.ErrConflict) {
		t.Fatalf("want ErrConflict, got %v", err)
	}
}

func TestBinStats(t *testing.T) {
	svc := seeded(t)
	if got := svc.BinStats().Count; got != 3 {
		t.Fatalf("count = %d", got)
	}
}

func TestBinAPI(t *testing.T) {
	h := httpapi.New(seeded(t))
	rec := call(t, h, http.MethodPost, "/bins", service.SampleBin(15))
	if rec.Code != http.StatusCreated {
		t.Fatalf("POST = %d %s", rec.Code, rec.Body)
	}
	var created model.Bin
	if err := json.Unmarshal(rec.Body.Bytes(), &created); err != nil {
		t.Fatalf("decode: %v", err)
	}
	path := fmt.Sprintf("/bins/%d", created.ID)
	if rec := call(t, h, http.MethodGet, path, nil); rec.Code != http.StatusOK {
		t.Fatalf("GET = %d", rec.Code)
	}
	if rec := call(t, h, http.MethodGet, "/bins?size=2&page=1", nil); rec.Code != http.StatusOK {
		t.Fatalf("list = %d", rec.Code)
	}
	if rec := call(t, h, http.MethodGet, "/bins/stats", nil); rec.Code != http.StatusOK {
		t.Fatalf("stats = %d", rec.Code)
	}
	if rec := call(t, h, http.MethodPost, "/bins", map[string]int{"no_such_field": 1}); rec.Code != http.StatusBadRequest {
		t.Fatalf("bad POST = %d", rec.Code)
	}
	if rec := call(t, h, http.MethodDelete, path, nil); rec.Code != http.StatusNoContent {
		t.Fatalf("DELETE = %d", rec.Code)
	}
	if rec := call(t, h, http.MethodGet, path, nil); rec.Code != http.StatusNotFound {
		t.Fatalf("GET after delete = %d", rec.Code)
	}
}

func TestStockMovementCreateAndGet(t *testing.T) {
	svc := seeded(t)
	created, err := svc.CreateStockMovement(service.SampleStockMovement(10))
	if err != nil {
		t.Fatalf("create: %v", err)
	}
	got, err := svc.GetStockMovement(created.ID)
	if err != nil || got != created {
		t.Fatalf("get = %+v, %v; want %+v", got, err, created)
	}
	if n := len(svc.ListStockMovements()); n != 4 {
		t.Fatalf("list has %d records, want 4", n)
	}
}

func TestStockMovementMissing(t *testing.T) {
	svc := seeded(t)
	if _, err := svc.GetStockMovement(9999); !errors.Is(err, service.ErrNotFound) {
		t.Fatalf("want ErrNotFound, got %v", err)
	}
}

func TestStockMovementRejectsBadProductID(t *testing.T) {
	svc := seeded(t)
	item := service.SampleStockMovement(12)
	item.ProductID = 0
	_, err := svc.CreateStockMovement(item)
	wantField(t, err, "product_id")
}

func TestStockMovementRejectsBadBinID(t *testing.T) {
	svc := seeded(t)
	item := service.SampleStockMovement(12)
	item.BinID = 0
	_, err := svc.CreateStockMovement(item)
	wantField(t, err, "bin_id")
}

func TestStockMovementRejectsBadQuantity(t *testing.T) {
	svc := seeded(t)
	item := service.SampleStockMovement(12)
	item.Quantity = -1
	_, err := svc.CreateStockMovement(item)
	wantField(t, err, "quantity")
}

func TestStockMovementRejectsBadMoved(t *testing.T) {
	svc := seeded(t)
	item := service.SampleStockMovement(12)
	item.Moved = "2026-02-30"
	_, err := svc.CreateStockMovement(item)
	wantField(t, err, "moved")
}

func TestStockMovementRejectsBadReason(t *testing.T) {
	svc := seeded(t)
	item := service.SampleStockMovement(12)
	item.Reason = "nope"
	_, err := svc.CreateStockMovement(item)
	wantField(t, err, "reason")
}

func TestStockMovementRejectsBadReference(t *testing.T) {
	svc := seeded(t)
	item := service.SampleStockMovement(12)
	item.Reference = ""
	_, err := svc.CreateStockMovement(item)
	wantField(t, err, "reference")
}

func TestStockMovementProductIDMustExist(t *testing.T) {
	svc := seeded(t)
	item := service.SampleStockMovement(13)
	item.ProductID = 9999
	if _, err := svc.CreateStockMovement(item); !errors.Is(err, service.ErrNotFound) {
		t.Fatalf("want ErrNotFound, got %v", err)
	}
}

func TestStockMovementBinIDMustExist(t *testing.T) {
	svc := seeded(t)
	item := service.SampleStockMovement(13)
	item.BinID = 9999
	if _, err := svc.CreateStockMovement(item); !errors.Is(err, service.ErrNotFound) {
		t.Fatalf("want ErrNotFound, got %v", err)
	}
}

func TestAdjustStockMovementQuantity(t *testing.T) {
	svc := seeded(t)
	before, _ := svc.GetStockMovement(1)
	after, err := svc.AdjustStockMovementQuantity(1, 2)
	if err != nil || after.Quantity != before.Quantity+2 {
		t.Fatalf("adjust = %v, %v", after.Quantity, err)
	}
	_, err = svc.AdjustStockMovementQuantity(1, -(after.Quantity + 100))
	wantField(t, err, "quantity")
}

func TestStockMovementMovedRanges(t *testing.T) {
	svc := seeded(t)
	day := service.SampleStockMovement(2).Moved
	total := len(svc.StockMovements.MovedBefore(day)) + len(svc.StockMovements.MovedOn(day)) + len(svc.StockMovements.MovedAfter(day))
	if total != svc.StockMovements.Count() {
		t.Fatalf("ranges cover %d of %d records", total, svc.StockMovements.Count())
	}
}

func TestSetStockMovementReason(t *testing.T) {
	svc := seeded(t)
	last := model.StockMovementReasonValues[len(model.StockMovementReasonValues)-1]
	item, err := svc.SetStockMovementReason(1, last)
	if err != nil || item.Reason != last {
		t.Fatalf("set = %v, %v", item.Reason, err)
	}
	if got, want := svc.StockMovements.CountByReason()[last], len(svc.StockMovements.WithReason(last)); got != want {
		t.Fatalf("count %d != %d", got, want)
	}
}

func TestSearchStockMovementReference(t *testing.T) {
	svc := seeded(t)
	target, _ := svc.GetStockMovement(2)
	for _, item := range svc.StockMovements.SearchReference(strings.ToUpper(target.Reference)) {
		if item.ID == target.ID {
			return
		}
	}
	t.Fatalf("search did not find %q", target.Reference)
}

func TestDeleteStockMovement(t *testing.T) {
	svc := seeded(t)
	item, err := svc.CreateStockMovement(service.SampleStockMovement(14))
	if err != nil {
		t.Fatalf("create: %v", err)
	}
	if err := svc.DeleteStockMovement(item.ID); err != nil {
		t.Fatalf("delete: %v", err)
	}
	if _, err := svc.GetStockMovement(item.ID); !errors.Is(err, service.ErrNotFound) {
		t.Fatalf("still there: %v", err)
	}
}

func TestStockMovementStats(t *testing.T) {
	svc := seeded(t)
	if got := svc.StockMovementStats().Count; got != 3 {
		t.Fatalf("count = %d", got)
	}
}

func TestStockMovementAPI(t *testing.T) {
	h := httpapi.New(seeded(t))
	rec := call(t, h, http.MethodPost, "/stock-movements", service.SampleStockMovement(15))
	if rec.Code != http.StatusCreated {
		t.Fatalf("POST = %d %s", rec.Code, rec.Body)
	}
	var created model.StockMovement
	if err := json.Unmarshal(rec.Body.Bytes(), &created); err != nil {
		t.Fatalf("decode: %v", err)
	}
	path := fmt.Sprintf("/stock-movements/%d", created.ID)
	if rec := call(t, h, http.MethodGet, path, nil); rec.Code != http.StatusOK {
		t.Fatalf("GET = %d", rec.Code)
	}
	if rec := call(t, h, http.MethodGet, "/stock-movements?size=2&page=1", nil); rec.Code != http.StatusOK {
		t.Fatalf("list = %d", rec.Code)
	}
	if rec := call(t, h, http.MethodGet, "/stock-movements/stats", nil); rec.Code != http.StatusOK {
		t.Fatalf("stats = %d", rec.Code)
	}
	if rec := call(t, h, http.MethodPost, "/stock-movements", map[string]int{"no_such_field": 1}); rec.Code != http.StatusBadRequest {
		t.Fatalf("bad POST = %d", rec.Code)
	}
	if rec := call(t, h, http.MethodDelete, path, nil); rec.Code != http.StatusNoContent {
		t.Fatalf("DELETE = %d", rec.Code)
	}
	if rec := call(t, h, http.MethodGet, path, nil); rec.Code != http.StatusNotFound {
		t.Fatalf("GET after delete = %d", rec.Code)
	}
}

func TestPurchaseOrderCreateAndGet(t *testing.T) {
	svc := seeded(t)
	created, err := svc.CreatePurchaseOrder(service.SamplePurchaseOrder(10))
	if err != nil {
		t.Fatalf("create: %v", err)
	}
	got, err := svc.GetPurchaseOrder(created.ID)
	if err != nil || got != created {
		t.Fatalf("get = %+v, %v; want %+v", got, err, created)
	}
	if n := len(svc.ListPurchaseOrders()); n != 4 {
		t.Fatalf("list has %d records, want 4", n)
	}
}

func TestPurchaseOrderMissing(t *testing.T) {
	svc := seeded(t)
	if _, err := svc.GetPurchaseOrder(9999); !errors.Is(err, service.ErrNotFound) {
		t.Fatalf("want ErrNotFound, got %v", err)
	}
}

func TestPurchaseOrderRejectsBadSupplierID(t *testing.T) {
	svc := seeded(t)
	item := service.SamplePurchaseOrder(12)
	item.SupplierID = 0
	_, err := svc.CreatePurchaseOrder(item)
	wantField(t, err, "supplier_id")
}

func TestPurchaseOrderRejectsBadOrdered(t *testing.T) {
	svc := seeded(t)
	item := service.SamplePurchaseOrder(12)
	item.Ordered = "2026-02-30"
	_, err := svc.CreatePurchaseOrder(item)
	wantField(t, err, "ordered")
}

func TestPurchaseOrderRejectsBadExpected(t *testing.T) {
	svc := seeded(t)
	item := service.SamplePurchaseOrder(12)
	item.Expected = "2026-02-30"
	_, err := svc.CreatePurchaseOrder(item)
	wantField(t, err, "expected")
}

func TestPurchaseOrderRejectsBadTotal(t *testing.T) {
	svc := seeded(t)
	item := service.SamplePurchaseOrder(12)
	item.Total = -5
	_, err := svc.CreatePurchaseOrder(item)
	wantField(t, err, "total")
}

func TestPurchaseOrderRejectsBadStatus(t *testing.T) {
	svc := seeded(t)
	item := service.SamplePurchaseOrder(12)
	item.Status = "nope"
	_, err := svc.CreatePurchaseOrder(item)
	wantField(t, err, "status")
}

func TestPurchaseOrderRejectsBadNotes(t *testing.T) {
	svc := seeded(t)
	item := service.SamplePurchaseOrder(12)
	item.Notes = strings.Repeat("x", 3000)
	_, err := svc.CreatePurchaseOrder(item)
	wantField(t, err, "notes")
}

func TestPurchaseOrderSupplierIDMustExist(t *testing.T) {
	svc := seeded(t)
	item := service.SamplePurchaseOrder(13)
	item.SupplierID = 9999
	if _, err := svc.CreatePurchaseOrder(item); !errors.Is(err, service.ErrNotFound) {
		t.Fatalf("want ErrNotFound, got %v", err)
	}
}

func TestPurchaseOrderOrderedRanges(t *testing.T) {
	svc := seeded(t)
	day := service.SamplePurchaseOrder(2).Ordered
	total := len(svc.PurchaseOrders.OrderedBefore(day)) + len(svc.PurchaseOrders.OrderedOn(day)) + len(svc.PurchaseOrders.OrderedAfter(day))
	if total != svc.PurchaseOrders.Count() {
		t.Fatalf("ranges cover %d of %d records", total, svc.PurchaseOrders.Count())
	}
}

func TestPurchaseOrderExpectedRanges(t *testing.T) {
	svc := seeded(t)
	day := service.SamplePurchaseOrder(2).Expected
	total := len(svc.PurchaseOrders.ExpectedBefore(day)) + len(svc.PurchaseOrders.ExpectedOn(day)) + len(svc.PurchaseOrders.ExpectedAfter(day))
	if total != svc.PurchaseOrders.Count() {
		t.Fatalf("ranges cover %d of %d records", total, svc.PurchaseOrders.Count())
	}
}

func TestAdjustPurchaseOrderTotal(t *testing.T) {
	svc := seeded(t)
	before, _ := svc.GetPurchaseOrder(1)
	after, err := svc.AdjustPurchaseOrderTotal(1, 1.5)
	if err != nil || after.Total-before.Total < 1.49 || after.Total-before.Total > 1.51 {
		t.Fatalf("adjust = %v, %v", after.Total, err)
	}
}

func TestSetPurchaseOrderStatus(t *testing.T) {
	svc := seeded(t)
	last := model.PurchaseOrderStatusValues[len(model.PurchaseOrderStatusValues)-1]
	item, err := svc.SetPurchaseOrderStatus(1, last)
	if err != nil || item.Status != last {
		t.Fatalf("set = %v, %v", item.Status, err)
	}
	if got, want := svc.PurchaseOrders.CountByStatus()[last], len(svc.PurchaseOrders.WithStatus(last)); got != want {
		t.Fatalf("count %d != %d", got, want)
	}
}

func TestSearchPurchaseOrderNotes(t *testing.T) {
	svc := seeded(t)
	target, _ := svc.GetPurchaseOrder(2)
	for _, item := range svc.PurchaseOrders.SearchNotes(strings.ToUpper(target.Notes)) {
		if item.ID == target.ID {
			return
		}
	}
	t.Fatalf("search did not find %q", target.Notes)
}

func TestDeletePurchaseOrder(t *testing.T) {
	svc := seeded(t)
	item, err := svc.CreatePurchaseOrder(service.SamplePurchaseOrder(14))
	if err != nil {
		t.Fatalf("create: %v", err)
	}
	if err := svc.DeletePurchaseOrder(item.ID); err != nil {
		t.Fatalf("delete: %v", err)
	}
	if _, err := svc.GetPurchaseOrder(item.ID); !errors.Is(err, service.ErrNotFound) {
		t.Fatalf("still there: %v", err)
	}
}

func TestPurchaseOrderStats(t *testing.T) {
	svc := seeded(t)
	if got := svc.PurchaseOrderStats().Count; got != 3 {
		t.Fatalf("count = %d", got)
	}
}

func TestPurchaseOrderAPI(t *testing.T) {
	h := httpapi.New(seeded(t))
	rec := call(t, h, http.MethodPost, "/purchase-orders", service.SamplePurchaseOrder(15))
	if rec.Code != http.StatusCreated {
		t.Fatalf("POST = %d %s", rec.Code, rec.Body)
	}
	var created model.PurchaseOrder
	if err := json.Unmarshal(rec.Body.Bytes(), &created); err != nil {
		t.Fatalf("decode: %v", err)
	}
	path := fmt.Sprintf("/purchase-orders/%d", created.ID)
	if rec := call(t, h, http.MethodGet, path, nil); rec.Code != http.StatusOK {
		t.Fatalf("GET = %d", rec.Code)
	}
	if rec := call(t, h, http.MethodGet, "/purchase-orders?size=2&page=1", nil); rec.Code != http.StatusOK {
		t.Fatalf("list = %d", rec.Code)
	}
	if rec := call(t, h, http.MethodGet, "/purchase-orders/stats", nil); rec.Code != http.StatusOK {
		t.Fatalf("stats = %d", rec.Code)
	}
	if rec := call(t, h, http.MethodPost, "/purchase-orders", map[string]int{"no_such_field": 1}); rec.Code != http.StatusBadRequest {
		t.Fatalf("bad POST = %d", rec.Code)
	}
	if rec := call(t, h, http.MethodDelete, path, nil); rec.Code != http.StatusNoContent {
		t.Fatalf("DELETE = %d", rec.Code)
	}
	if rec := call(t, h, http.MethodGet, path, nil); rec.Code != http.StatusNotFound {
		t.Fatalf("GET after delete = %d", rec.Code)
	}
}

func TestStockCountCreateAndGet(t *testing.T) {
	svc := seeded(t)
	created, err := svc.CreateStockCount(service.SampleStockCount(10))
	if err != nil {
		t.Fatalf("create: %v", err)
	}
	got, err := svc.GetStockCount(created.ID)
	if err != nil || got != created {
		t.Fatalf("get = %+v, %v; want %+v", got, err, created)
	}
	if n := len(svc.ListStockCounts()); n != 4 {
		t.Fatalf("list has %d records, want 4", n)
	}
}

func TestStockCountMissing(t *testing.T) {
	svc := seeded(t)
	if _, err := svc.GetStockCount(9999); !errors.Is(err, service.ErrNotFound) {
		t.Fatalf("want ErrNotFound, got %v", err)
	}
}

func TestStockCountRejectsBadBinID(t *testing.T) {
	svc := seeded(t)
	item := service.SampleStockCount(12)
	item.BinID = 0
	_, err := svc.CreateStockCount(item)
	wantField(t, err, "bin_id")
}

func TestStockCountRejectsBadProductID(t *testing.T) {
	svc := seeded(t)
	item := service.SampleStockCount(12)
	item.ProductID = 0
	_, err := svc.CreateStockCount(item)
	wantField(t, err, "product_id")
}

func TestStockCountRejectsBadCounted(t *testing.T) {
	svc := seeded(t)
	item := service.SampleStockCount(12)
	item.Counted = "2026-02-30"
	_, err := svc.CreateStockCount(item)
	wantField(t, err, "counted")
}

func TestStockCountRejectsBadExpected(t *testing.T) {
	svc := seeded(t)
	item := service.SampleStockCount(12)
	item.Expected = -1
	_, err := svc.CreateStockCount(item)
	wantField(t, err, "expected")
}

func TestStockCountRejectsBadFound(t *testing.T) {
	svc := seeded(t)
	item := service.SampleStockCount(12)
	item.Found = -1
	_, err := svc.CreateStockCount(item)
	wantField(t, err, "found")
}

func TestStockCountRejectsBadCounter(t *testing.T) {
	svc := seeded(t)
	item := service.SampleStockCount(12)
	item.Counter = ""
	_, err := svc.CreateStockCount(item)
	wantField(t, err, "counter")
}

func TestStockCountBinIDMustExist(t *testing.T) {
	svc := seeded(t)
	item := service.SampleStockCount(13)
	item.BinID = 9999
	if _, err := svc.CreateStockCount(item); !errors.Is(err, service.ErrNotFound) {
		t.Fatalf("want ErrNotFound, got %v", err)
	}
}

func TestStockCountProductIDMustExist(t *testing.T) {
	svc := seeded(t)
	item := service.SampleStockCount(13)
	item.ProductID = 9999
	if _, err := svc.CreateStockCount(item); !errors.Is(err, service.ErrNotFound) {
		t.Fatalf("want ErrNotFound, got %v", err)
	}
}

func TestStockCountCountedRanges(t *testing.T) {
	svc := seeded(t)
	day := service.SampleStockCount(2).Counted
	total := len(svc.StockCounts.CountedBefore(day)) + len(svc.StockCounts.CountedOn(day)) + len(svc.StockCounts.CountedAfter(day))
	if total != svc.StockCounts.Count() {
		t.Fatalf("ranges cover %d of %d records", total, svc.StockCounts.Count())
	}
}

func TestAdjustStockCountExpected(t *testing.T) {
	svc := seeded(t)
	before, _ := svc.GetStockCount(1)
	after, err := svc.AdjustStockCountExpected(1, 2)
	if err != nil || after.Expected != before.Expected+2 {
		t.Fatalf("adjust = %v, %v", after.Expected, err)
	}
	_, err = svc.AdjustStockCountExpected(1, -(after.Expected + 100))
	wantField(t, err, "expected")
}

func TestAdjustStockCountFound(t *testing.T) {
	svc := seeded(t)
	before, _ := svc.GetStockCount(1)
	after, err := svc.AdjustStockCountFound(1, 2)
	if err != nil || after.Found != before.Found+2 {
		t.Fatalf("adjust = %v, %v", after.Found, err)
	}
	_, err = svc.AdjustStockCountFound(1, -(after.Found + 100))
	wantField(t, err, "found")
}

func TestSearchStockCountCounter(t *testing.T) {
	svc := seeded(t)
	target, _ := svc.GetStockCount(2)
	for _, item := range svc.StockCounts.SearchCounter(strings.ToUpper(target.Counter)) {
		if item.ID == target.ID {
			return
		}
	}
	t.Fatalf("search did not find %q", target.Counter)
}

func TestDeleteStockCount(t *testing.T) {
	svc := seeded(t)
	item, err := svc.CreateStockCount(service.SampleStockCount(14))
	if err != nil {
		t.Fatalf("create: %v", err)
	}
	if err := svc.DeleteStockCount(item.ID); err != nil {
		t.Fatalf("delete: %v", err)
	}
	if _, err := svc.GetStockCount(item.ID); !errors.Is(err, service.ErrNotFound) {
		t.Fatalf("still there: %v", err)
	}
}

func TestStockCountStats(t *testing.T) {
	svc := seeded(t)
	if got := svc.StockCountStats().Count; got != 3 {
		t.Fatalf("count = %d", got)
	}
}

func TestStockCountAPI(t *testing.T) {
	h := httpapi.New(seeded(t))
	rec := call(t, h, http.MethodPost, "/stock-counts", service.SampleStockCount(15))
	if rec.Code != http.StatusCreated {
		t.Fatalf("POST = %d %s", rec.Code, rec.Body)
	}
	var created model.StockCount
	if err := json.Unmarshal(rec.Body.Bytes(), &created); err != nil {
		t.Fatalf("decode: %v", err)
	}
	path := fmt.Sprintf("/stock-counts/%d", created.ID)
	if rec := call(t, h, http.MethodGet, path, nil); rec.Code != http.StatusOK {
		t.Fatalf("GET = %d", rec.Code)
	}
	if rec := call(t, h, http.MethodGet, "/stock-counts?size=2&page=1", nil); rec.Code != http.StatusOK {
		t.Fatalf("list = %d", rec.Code)
	}
	if rec := call(t, h, http.MethodGet, "/stock-counts/stats", nil); rec.Code != http.StatusOK {
		t.Fatalf("stats = %d", rec.Code)
	}
	if rec := call(t, h, http.MethodPost, "/stock-counts", map[string]int{"no_such_field": 1}); rec.Code != http.StatusBadRequest {
		t.Fatalf("bad POST = %d", rec.Code)
	}
	if rec := call(t, h, http.MethodDelete, path, nil); rec.Code != http.StatusNoContent {
		t.Fatalf("DELETE = %d", rec.Code)
	}
	if rec := call(t, h, http.MethodGet, path, nil); rec.Code != http.StatusNotFound {
		t.Fatalf("GET after delete = %d", rec.Code)
	}
}

func TestDocumentCreateAndGet(t *testing.T) {
	svc := seeded(t)
	created, err := svc.CreateDocument(service.SampleDocument(10))
	if err != nil {
		t.Fatalf("create: %v", err)
	}
	got, err := svc.GetDocument(created.ID)
	if err != nil || got != created {
		t.Fatalf("get = %+v, %v; want %+v", got, err, created)
	}
	if n := len(svc.ListDocuments()); n != 4 {
		t.Fatalf("list has %d records, want 4", n)
	}
}

func TestDocumentMissing(t *testing.T) {
	svc := seeded(t)
	if _, err := svc.GetDocument(9999); !errors.Is(err, service.ErrNotFound) {
		t.Fatalf("want ErrNotFound, got %v", err)
	}
}

func TestDocumentRejectsBadSupplierID(t *testing.T) {
	svc := seeded(t)
	item := service.SampleDocument(12)
	item.SupplierID = 0
	_, err := svc.CreateDocument(item)
	wantField(t, err, "supplier_id")
}

func TestDocumentRejectsBadTitle(t *testing.T) {
	svc := seeded(t)
	item := service.SampleDocument(12)
	item.Title = ""
	_, err := svc.CreateDocument(item)
	wantField(t, err, "title")
}

func TestDocumentRejectsBadPages(t *testing.T) {
	svc := seeded(t)
	item := service.SampleDocument(12)
	item.Pages = -1
	_, err := svc.CreateDocument(item)
	wantField(t, err, "pages")
}

func TestDocumentRejectsBadVersion(t *testing.T) {
	svc := seeded(t)
	item := service.SampleDocument(12)
	item.Version = -1
	_, err := svc.CreateDocument(item)
	wantField(t, err, "version")
}

func TestDocumentRejectsBadIssued(t *testing.T) {
	svc := seeded(t)
	item := service.SampleDocument(12)
	item.Issued = "2026-02-30"
	_, err := svc.CreateDocument(item)
	wantField(t, err, "issued")
}

func TestDocumentSupplierIDMustExist(t *testing.T) {
	svc := seeded(t)
	item := service.SampleDocument(13)
	item.SupplierID = 9999
	if _, err := svc.CreateDocument(item); !errors.Is(err, service.ErrNotFound) {
		t.Fatalf("want ErrNotFound, got %v", err)
	}
}

func TestSearchDocumentTitle(t *testing.T) {
	svc := seeded(t)
	target, _ := svc.GetDocument(2)
	for _, item := range svc.Documents.SearchTitle(strings.ToUpper(target.Title)) {
		if item.ID == target.ID {
			return
		}
	}
	t.Fatalf("search did not find %q", target.Title)
}

func TestAdjustDocumentPages(t *testing.T) {
	svc := seeded(t)
	before, _ := svc.GetDocument(1)
	after, err := svc.AdjustDocumentPages(1, 2)
	if err != nil || after.Pages != before.Pages+2 {
		t.Fatalf("adjust = %v, %v", after.Pages, err)
	}
	_, err = svc.AdjustDocumentPages(1, -(after.Pages + 100))
	wantField(t, err, "pages")
}

func TestToggleDocumentSigned(t *testing.T) {
	svc := seeded(t)
	before, _ := svc.GetDocument(1)
	after, err := svc.ToggleDocumentSigned(1)
	if err != nil || after.Signed == before.Signed {
		t.Fatalf("toggle = %v, %v", after.Signed, err)
	}
}

func TestAdjustDocumentVersion(t *testing.T) {
	svc := seeded(t)
	before, _ := svc.GetDocument(1)
	after, err := svc.AdjustDocumentVersion(1, 2)
	if err != nil || after.Version != before.Version+2 {
		t.Fatalf("adjust = %v, %v", after.Version, err)
	}
	_, err = svc.AdjustDocumentVersion(1, -(after.Version + 100))
	wantField(t, err, "version")
}

func TestDocumentIssuedRanges(t *testing.T) {
	svc := seeded(t)
	day := service.SampleDocument(2).Issued
	total := len(svc.Documents.IssuedBefore(day)) + len(svc.Documents.IssuedOn(day)) + len(svc.Documents.IssuedAfter(day))
	if total != svc.Documents.Count() {
		t.Fatalf("ranges cover %d of %d records", total, svc.Documents.Count())
	}
}

func TestDeleteDocument(t *testing.T) {
	svc := seeded(t)
	item, err := svc.CreateDocument(service.SampleDocument(14))
	if err != nil {
		t.Fatalf("create: %v", err)
	}
	if err := svc.DeleteDocument(item.ID); err != nil {
		t.Fatalf("delete: %v", err)
	}
	if _, err := svc.GetDocument(item.ID); !errors.Is(err, service.ErrNotFound) {
		t.Fatalf("still there: %v", err)
	}
}

func TestDocumentStats(t *testing.T) {
	svc := seeded(t)
	if got := svc.DocumentStats().Count; got != 3 {
		t.Fatalf("count = %d", got)
	}
}

func TestDocumentAPI(t *testing.T) {
	h := httpapi.New(seeded(t))
	rec := call(t, h, http.MethodPost, "/documents", service.SampleDocument(15))
	if rec.Code != http.StatusCreated {
		t.Fatalf("POST = %d %s", rec.Code, rec.Body)
	}
	var created model.Document
	if err := json.Unmarshal(rec.Body.Bytes(), &created); err != nil {
		t.Fatalf("decode: %v", err)
	}
	path := fmt.Sprintf("/documents/%d", created.ID)
	if rec := call(t, h, http.MethodGet, path, nil); rec.Code != http.StatusOK {
		t.Fatalf("GET = %d", rec.Code)
	}
	if rec := call(t, h, http.MethodGet, "/documents?size=2&page=1", nil); rec.Code != http.StatusOK {
		t.Fatalf("list = %d", rec.Code)
	}
	if rec := call(t, h, http.MethodGet, "/documents/stats", nil); rec.Code != http.StatusOK {
		t.Fatalf("stats = %d", rec.Code)
	}
	if rec := call(t, h, http.MethodPost, "/documents", map[string]int{"no_such_field": 1}); rec.Code != http.StatusBadRequest {
		t.Fatalf("bad POST = %d", rec.Code)
	}
	if rec := call(t, h, http.MethodDelete, path, nil); rec.Code != http.StatusNoContent {
		t.Fatalf("DELETE = %d", rec.Code)
	}
	if rec := call(t, h, http.MethodGet, path, nil); rec.Code != http.StatusNotFound {
		t.Fatalf("GET after delete = %d", rec.Code)
	}
}

func TestNotificationCreateAndGet(t *testing.T) {
	svc := seeded(t)
	created, err := svc.CreateNotification(service.SampleNotification(10))
	if err != nil {
		t.Fatalf("create: %v", err)
	}
	got, err := svc.GetNotification(created.ID)
	if err != nil || got != created {
		t.Fatalf("get = %+v, %v; want %+v", got, err, created)
	}
	if n := len(svc.ListNotifications()); n != 4 {
		t.Fatalf("list has %d records, want 4", n)
	}
}

func TestNotificationMissing(t *testing.T) {
	svc := seeded(t)
	if _, err := svc.GetNotification(9999); !errors.Is(err, service.ErrNotFound) {
		t.Fatalf("want ErrNotFound, got %v", err)
	}
}

func TestNotificationRejectsBadRecipient(t *testing.T) {
	svc := seeded(t)
	item := service.SampleNotification(12)
	item.Recipient = "not-an-email"
	_, err := svc.CreateNotification(item)
	wantField(t, err, "recipient")
}

func TestNotificationRejectsBadTitle(t *testing.T) {
	svc := seeded(t)
	item := service.SampleNotification(12)
	item.Title = ""
	_, err := svc.CreateNotification(item)
	wantField(t, err, "title")
}

func TestNotificationRejectsBadSent(t *testing.T) {
	svc := seeded(t)
	item := service.SampleNotification(12)
	item.Sent = "2026-02-30"
	_, err := svc.CreateNotification(item)
	wantField(t, err, "sent")
}

func TestNotificationRejectsBadChannel(t *testing.T) {
	svc := seeded(t)
	item := service.SampleNotification(12)
	item.Channel = "nope"
	_, err := svc.CreateNotification(item)
	wantField(t, err, "channel")
}

func TestSearchNotificationRecipient(t *testing.T) {
	svc := seeded(t)
	target, _ := svc.GetNotification(2)
	for _, item := range svc.Notifications.SearchRecipient(strings.ToUpper(target.Recipient)) {
		if item.ID == target.ID {
			return
		}
	}
	t.Fatalf("search did not find %q", target.Recipient)
}

func TestSearchNotificationTitle(t *testing.T) {
	svc := seeded(t)
	target, _ := svc.GetNotification(2)
	for _, item := range svc.Notifications.SearchTitle(strings.ToUpper(target.Title)) {
		if item.ID == target.ID {
			return
		}
	}
	t.Fatalf("search did not find %q", target.Title)
}

func TestNotificationSentRanges(t *testing.T) {
	svc := seeded(t)
	day := service.SampleNotification(2).Sent
	total := len(svc.Notifications.SentBefore(day)) + len(svc.Notifications.SentOn(day)) + len(svc.Notifications.SentAfter(day))
	if total != svc.Notifications.Count() {
		t.Fatalf("ranges cover %d of %d records", total, svc.Notifications.Count())
	}
}

func TestSetNotificationChannel(t *testing.T) {
	svc := seeded(t)
	last := model.NotificationChannelValues[len(model.NotificationChannelValues)-1]
	item, err := svc.SetNotificationChannel(1, last)
	if err != nil || item.Channel != last {
		t.Fatalf("set = %v, %v", item.Channel, err)
	}
	if got, want := svc.Notifications.CountByChannel()[last], len(svc.Notifications.WithChannel(last)); got != want {
		t.Fatalf("count %d != %d", got, want)
	}
}

func TestToggleNotificationRead(t *testing.T) {
	svc := seeded(t)
	before, _ := svc.GetNotification(1)
	after, err := svc.ToggleNotificationRead(1)
	if err != nil || after.Read == before.Read {
		t.Fatalf("toggle = %v, %v", after.Read, err)
	}
}

func TestDeleteNotification(t *testing.T) {
	svc := seeded(t)
	item, err := svc.CreateNotification(service.SampleNotification(14))
	if err != nil {
		t.Fatalf("create: %v", err)
	}
	if err := svc.DeleteNotification(item.ID); err != nil {
		t.Fatalf("delete: %v", err)
	}
	if _, err := svc.GetNotification(item.ID); !errors.Is(err, service.ErrNotFound) {
		t.Fatalf("still there: %v", err)
	}
}

func TestNotificationStats(t *testing.T) {
	svc := seeded(t)
	if got := svc.NotificationStats().Count; got != 3 {
		t.Fatalf("count = %d", got)
	}
}

func TestNotificationAPI(t *testing.T) {
	h := httpapi.New(seeded(t))
	rec := call(t, h, http.MethodPost, "/notifications", service.SampleNotification(15))
	if rec.Code != http.StatusCreated {
		t.Fatalf("POST = %d %s", rec.Code, rec.Body)
	}
	var created model.Notification
	if err := json.Unmarshal(rec.Body.Bytes(), &created); err != nil {
		t.Fatalf("decode: %v", err)
	}
	path := fmt.Sprintf("/notifications/%d", created.ID)
	if rec := call(t, h, http.MethodGet, path, nil); rec.Code != http.StatusOK {
		t.Fatalf("GET = %d", rec.Code)
	}
	if rec := call(t, h, http.MethodGet, "/notifications?size=2&page=1", nil); rec.Code != http.StatusOK {
		t.Fatalf("list = %d", rec.Code)
	}
	if rec := call(t, h, http.MethodGet, "/notifications/stats", nil); rec.Code != http.StatusOK {
		t.Fatalf("stats = %d", rec.Code)
	}
	if rec := call(t, h, http.MethodPost, "/notifications", map[string]int{"no_such_field": 1}); rec.Code != http.StatusBadRequest {
		t.Fatalf("bad POST = %d", rec.Code)
	}
	if rec := call(t, h, http.MethodDelete, path, nil); rec.Code != http.StatusNoContent {
		t.Fatalf("DELETE = %d", rec.Code)
	}
	if rec := call(t, h, http.MethodGet, path, nil); rec.Code != http.StatusNotFound {
		t.Fatalf("GET after delete = %d", rec.Code)
	}
}
