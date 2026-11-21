import type { Product } from "../types";
import { stockLevel } from "../utils/format";

const LABELS = {
  out: "Out of stock",
  low: "Low stock",
  ok: "In stock",
} as const;

interface StockBadgeProps {
  product: Product;
}

export function StockBadge({ product }: StockBadgeProps) {
  const level = stockLevel(product);
  return (
    <span className={`badge badge-${level}`} title={`${product.quantity} units`}>
      {LABELS[level]}
    </span>
  );
}
