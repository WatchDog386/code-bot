// Command server runs the Fleet Management API on http://127.0.0.1:8080
package main

import (
	"log"
	"net"
	"net/http"
	"strconv"

	"fleet-api/internal/config"
	"fleet-api/internal/httpapi"
	"fleet-api/internal/service"
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
	log.Printf("Fleet Management API on http://%s (Ctrl+C to stop)", addr)
	log.Fatal(http.ListenAndServe(addr, httpapi.New(svc)))
}
