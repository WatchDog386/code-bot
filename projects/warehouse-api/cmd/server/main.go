// Command server runs the Warehouse Inventory API on http://127.0.0.1:8080
package main

import (
	"log"
	"net/http"

	"warehouse-api/internal/httpapi"
	"warehouse-api/internal/service"
)

func main() {
	svc := service.New()
	if err := svc.Seed(3); err != nil {
		log.Fatal(err)
	}
	addr := "127.0.0.1:8080"
	log.Printf("Warehouse Inventory API on http://%s (Ctrl+C to stop)", addr)
	log.Fatal(http.ListenAndServe(addr, httpapi.New(svc)))
}
