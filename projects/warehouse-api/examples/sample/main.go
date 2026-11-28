// Command sample prints one valid supplier record.
package main

import (
	"fmt"

	"warehouse-api/internal/service"
)

func main() {
	fmt.Printf("%+v\n", service.SampleSupplier(1))
}
