package model

import "strings"

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
