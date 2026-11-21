import { useCallback, useEffect, useMemo, useState } from "react";

import { inventoryApi } from "../api/client";
import type { InventoryFilters, Product, SortState } from "../types";
import { stockLevel } from "../utils/format";

const DEFAULT_FILTERS: InventoryFilters = {
  search: "",
  category: "all",
  lowStockOnly: false,
};

export function useInventory() {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filters, setFilters] = useState<InventoryFilters>(DEFAULT_FILTERS);
  const [sort, setSort] = useState<SortState>({ key: "name", direction: "asc" });

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      setProducts(await inventoryApi.list());
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load products");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const visible = useMemo(() => {
    const term = filters.search.trim().toLowerCase();
    const filtered = products.filter((p) => {
      if (filters.category !== "all" && p.category !== filters.category) {
        return false;
      }
      if (filters.lowStockOnly && stockLevel(p) === "ok") {
        return false;
      }
      return !term || p.name.toLowerCase().includes(term) || p.sku.includes(term);
    });

    const dir = sort.direction === "asc" ? 1 : -1;
    return [...filtered].sort((a, b) => {
      const av = a[sort.key];
      const bv = b[sort.key];
      if (av < bv) return -1 * dir;
      if (av > bv) return 1 * dir;
      return 0;
    });
  }, [products, filters, sort]);

  const updateQuantity = useCallback(async (id: string, quantity: number) => {
    const updated = await inventoryApi.updateQuantity(id, quantity);
    setProducts((prev) => prev.map((p) => (p.id === id ? updated : p)));
  }, []);

  const toggleSort = useCallback((key: keyof Product) => {
    setSort((prev) =>
      prev.key === key
        ? { key, direction: prev.direction === "asc" ? "desc" : "asc" }
        : { key, direction: "asc" }
    );
  }, []);

  return {
    products: visible,
    total: products.length,
    loading,
    error,
    filters,
    setFilters,
    sort,
    toggleSort,
    updateQuantity,
    reload: load,
  };
}
