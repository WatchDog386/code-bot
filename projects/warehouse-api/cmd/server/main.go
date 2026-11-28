// Command server runs the Warehouse Inventory API on http://127.0.0.1:8080
package main

import (
	"log"
	"net"
	"net/http"
	"strconv"

	"warehouse-api/internal/config"
	"warehouse-api/internal/httpapi"
	"warehouse-api/internal/service"
)

func main() {
	cfg, err := config.Load()
	if err != nil {
		log.Fatal(err)
	}
	svc := service.New()
	if err := svc.Seed(cfg.SeedSize); err != nil {
		log.Fatal(err)
	}
	addr := net.JoinHostPort(cfg.Host, strconv.Itoa(cfg.Port))
	log.Printf("Warehouse Inventory API on http://%s (Ctrl+C to stop)", addr)
	log.Fatal(http.ListenAndServe(addr, httpapi.New(svc)))
}
