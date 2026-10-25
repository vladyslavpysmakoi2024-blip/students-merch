import { api } from "@shared/api/instance";
import { FavoriteItem, OrderItem, OrderReceipt } from "@shared/types/api";

export const getFavorites = async (): Promise<FavoriteItem[]> => {
  const res = await api.get<FavoriteItem[]>("/favorite");
  return res.data;
};

export const addFavorite = async (clothingId: number) => {
  const res = await api.post("/favorite", { id_clothing: clothingId });
  return res.data;
};

export const removeFavorite = async (clothingId: number) => {
  const res = await api.delete(`/favorite/${clothingId}`);
  return res.data;
};

export const getOrders = async (): Promise<OrderItem[]> => {
  const res = await api.get<OrderItem[]>("/orders");
  return res.data;
};

export const getOrderDetail = async (
  orderId: number | string,
): Promise<OrderItem> => {
  const res = await api.get<OrderItem>(`/orders/${orderId}`);
  return res.data;
};

export const getOrderReceipt = async (
  orderId: number | string,
): Promise<OrderReceipt> => {
  const res = await api.get<OrderReceipt>(`/orders/${orderId}/receipt`);
  return res.data;
};

export const addToCart = async ({ clothingId }: { clothingId: number }) => {
  const res = await api.post("/cart", {
    id_clothing: clothingId,
    quantity: 1,
  });
  return res.data;
};
