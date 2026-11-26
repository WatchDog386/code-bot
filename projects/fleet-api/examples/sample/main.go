// Command sample prints one valid vehicle record.
package main

import (
	"fmt"

	"fleet-api/internal/service"
)

func main() {
	fmt.Printf("%+v\n", service.SampleVehicle(1))
}
