import type { Product, SortState } from "../types";
import { formatDate, formatPrice } from "../utils/format";
import { StockBadge } from "./StockBadge";

interface Column {
  key: keyof Product;
  label: string;
}

const COLUMNS: Column[] = [
  { key: "sku", label: "SKU" },
  { key: "name", label: "Product" },
  { key: "category", label: "Category" },
  { key: "price", label: "Price" },
  { key: "quantity", label: "Qty" },
  { key: "updatedAt", label: "Updated" },
];

interface ProductTableProps {
  products: Product[];
  sort: SortState;
  onSort: (key: keyof Product) => void;
  onAdjust: (id: string, quantity: number) => void;
}

export function ProductTable({ products, sort, onSort, onAdjust }: ProductTableProps) {
  if (products.length === 0) {
    return <p className="empty">No products match the current filters.</p>;
  }

  return (
    <table className="product-table">
      <thead>
        <tr>
          {COLUMNS.map((col) => (
            <th key={col.key} onClick={() => onSort(col.key)}>
              {col.label}
              {sort.key === col.key && (sort.direction === "asc" ? " ^" : " v")}
            </th>
          ))}
          <th>Status</th>
          <th />
        </tr>
      </thead>
      <tbody>
        {products.map((p) => (
          <tr key={p.id}>
            <td className="mono">{p.sku}</td>
            <td>{p.name}</td>
            <td>{p.category}</td>
            <td>{formatPrice(p.price)}</td>
            <td>{p.quantity}</td>
            <td>{formatDate(p.updatedAt)}</td>
            <td>
              <StockBadge product={p} />
            </td>
            <td className="actions">
              <button onClick={() => onAdjust(p.id, Math.max(0, p.quantity - 1))}>-</button>
              <button onClick={() => onAdjust(p.id, p.quantity + 1)}>+</button>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
