// Package httpapi serves the Fleet Management service as JSON over HTTP (net/http only).
//
// Every collection has GET (list, with filters, ?q= search, ?page=&size=), POST,
// GET /{id}, PATCH /{id}, DELETE /{id} and GET /stats.
package httpapi

import "fleet-api/internal/service"

// API answers HTTP requests using the service.
type API struct {
	svc *service.Service
}
