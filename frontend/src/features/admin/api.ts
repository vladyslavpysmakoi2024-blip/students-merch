import { api } from "@shared/api/instance";
import { ClothingItem, OrderItem, PromoItem } from "@shared/types/api";

export const getAdminClothing = async (): Promise<ClothingItem[]> => {
  const res = await api.get<ClothingItem[]>("/admin/clothing");
  return res.data;
};

export const createClothes = async (items: Record<string, unknown>[]) => {
  const res = await api.post("/admin/clothing/bulk", { items });
  return res.data;
};

export const updateClothes = async (data: Record<string, unknown>) => {
  const res = await api.patch("/admin/clothing/bulk", data);
  return res.data;
};

export const deleteClothes = async (ids: number[]) => {
  const res = await api.post("/admin/clothing/bulk-delete", { ids });
  return res.data;
};

export const updateClothing = async ({
  id,
  data,
}: {
  id: number;
  data: Record<string, unknown>;
}) => {
  const res = await api.put(`/admin/clothing/${id}`, data);
  return res.data;
};

export const uploadClothingPhoto = async (
  file: File,
): Promise<{ url: string }> => {
  const formData = new FormData();
  formData.append("file", file);
  const res = await api.post<{ url: string }>("/admin/clothing/photo", formData);
  return res.data;
};

export const getAdminPromos = async (): Promise<PromoItem[]> => {
  const res = await api.get<PromoItem[]>("/admin/promo");
  return res.data;
};

export const createPromo = async (data: Record<string, unknown>) => {
  const res = await api.post("/admin/promo", data);
  return res.data;
};

export const updatePromo = async ({
  id,
  data,
}: {
  id: number;
  data: Record<string, unknown>;
}) => {
  const res = await api.put(`/admin/promo/${id}`, data);
  return res.data;
};

export const deletePromo = async (id: number) => {
  const res = await api.delete(`/admin/promo/${id}`);
  return res.data;
};

export const getAdminOrders = async (): Promise<OrderItem[]> => {
  const res = await api.get<OrderItem[]>("/admin/orders");
  return res.data;
};
