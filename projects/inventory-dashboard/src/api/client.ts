import type { ApiError, Product } from "../types";

const BASE_URL = import.meta.env.VITE_API_URL ?? "/api";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });

  if (!res.ok) {
    const error: ApiError = {
      status: res.status,
      message: (await res.text()) || res.statusText,
    };
    throw error;
  }

  if (res.status === 204) {
    return undefined as T;
  }
  return res.json() as Promise<T>;
}

export const inventoryApi = {
  list: () => request<Product[]>("/products"),

  get: (id: string) => request<Product>(`/products/${id}`),

  updateQuantity: (id: string, quantity: number) =>
    request<Product>(`/products/${id}`, {
      method: "PATCH",
      body: JSON.stringify({ quantity }),
    }),

  remove: (id: string) =>
    request<void>(`/products/${id}`, { method: "DELETE" }),
};
