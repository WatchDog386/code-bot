import { ProductTable } from "./components/ProductTable";
import { useInventory } from "./hooks/useInventory";
import type { Category } from "./types";
import { formatPrice, inventoryValue } from "./utils/format";

const CATEGORIES: Array<Category | "all"> = [
  "all",
  "hardware",
  "software",
  "accessories",
  "services",
];

export default function App() {
  const inv = useInventory();

  return (
    <main className="container">
      <header className="toolbar">
        <h1>Inventory</h1>
        <span className="muted">
          {inv.products.length} of {inv.total} products
          {" - "}
          {formatPrice(inventoryValue(inv.products))} in stock
        </span>
        <button onClick={inv.reload} disabled={inv.loading}>
          Refresh
        </button>
      </header>

      <section className="filters">
        <input
          type="search"
          placeholder="Search by name or SKU"
          value={inv.filters.search}
          onChange={(e) => inv.setFilters({ ...inv.filters, search: e.target.value })}
        />
        <select
          value={inv.filters.category}
          onChange={(e) =>
            inv.setFilters({ ...inv.filters, category: e.target.value as Category | "all" })
          }
        >
          {CATEGORIES.map((c) => (
            <option key={c} value={c}>
              {c}
            </option>
          ))}
        </select>
        <label>
          <input
            type="checkbox"
            checked={inv.filters.lowStockOnly}
            onChange={(e) => inv.setFilters({ ...inv.filters, lowStockOnly: e.target.checked })}
          />
          Low stock only
        </label>
      </section>

      {inv.error && <div className="error">{inv.error}</div>}
      {inv.loading ? (
        <p className="muted">Loading products...</p>
      ) : (
        <ProductTable
          products={inv.products}
          sort={inv.sort}
          onSort={inv.toggleSort}
          onAdjust={inv.updateQuantity}
        />
      )}
    </main>
  );
}
