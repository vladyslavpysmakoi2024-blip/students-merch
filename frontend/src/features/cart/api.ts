import { api } from "@shared/api/instance";
import { CartItem, PromoItem } from "@shared/types/api";

export const getCart = async (): Promise<CartItem[]> => {
  const res = await api.get<CartItem[]>("/cart");
  return res.data;
};

export const updateCartItemQuantity = async ({
  cartId,
  quantity,
}: {
  cartId: number;
  quantity: number;
}) => {
  const res = await api.patch(`/cart/${cartId}`, { quantity });
  return res.data;
};

export const removeCartItem = async (cartId: number) => {
  const res = await api.delete(`/cart/${cartId}`);
  return res.data;
};

export const applyPromoCode = async (promo: string): Promise<PromoItem> => {
  const res = await api.post<PromoItem>("/promo/apply", { promo });
  return res.data;
};

export const addPackageToCart = async ({
  packageId,
  tshirtId,
  toteId,
}: {
  packageId?: string | number;
  tshirtId?: string | number;
  toteId?: string | number;
} = {}) => {
  const res = await api.post("/cart/package", {
    package_id: packageId,
    tshirt_id: tshirtId,
    tote_id: toteId,
  });
  return res.data;
};
