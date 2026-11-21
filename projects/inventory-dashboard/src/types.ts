export type Category = "hardware" | "software" | "accessories" | "services";

export interface Product {
  id: string;
  sku: string;
  name: string;
  category: Category;
  price: number;
  quantity: number;
  reorderLevel: number;
  updatedAt: string;
}

export type StockLevel = "out" | "low" | "ok";

export interface InventoryFilters {
  search: string;
  category: Category | "all";
  lowStockOnly: boolean;
}

export interface SortState {
  key: keyof Product;
  direction: "asc" | "desc";
}

export interface ApiError {
  status: number;
  message: string;
}
