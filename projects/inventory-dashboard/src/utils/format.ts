import type { Product, StockLevel } from "../types";

const currency = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
});

export function formatPrice(value: number): string {
  return currency.format(value);
}

export function formatDate(iso: string): string {
  const date = new Date(iso);
  return date.toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

export function stockLevel(product: Product): StockLevel {
  if (product.quantity === 0) return "out";
  if (product.quantity <= product.reorderLevel) return "low";
  return "ok";
}

export function inventoryValue(products: Product[]): number {
  return products.reduce((sum, p) => sum + p.price * p.quantity, 0);
}
