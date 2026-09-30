import { api } from "../../shared/api/instance";

export const getCart = async () => {
  const res = await api.get("/cart");
  return res.data;
};

export const updateCartItemQuantity = async ({ cartId, quantity }) => {
  const res = await api.patch(`/cart/${cartId}`, { quantity });
  return res.data;
};

export const removeCartItem = async (cartId) => {
  const res = await api.delete(`/cart/${cartId}`);
  return res.data;
};

export const applyPromoCode = async (promo) => {
  const res = await api.post("/promo/apply", { promo });
  return res.data;
};

export const addPackageToCart = async ({ packageId, tshirtId, toteId } = {}) => {
  const res = await api.post("/cart/package", {
    package_id: packageId,
    tshirt_id: tshirtId,
    tote_id: toteId,
  });
  return res.data;
};
