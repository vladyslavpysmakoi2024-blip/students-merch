import { api } from "../../shared/api/instance";

export const getFavorites = async () => {
  const res = await api.get("/favorites");
  return res.data;
};

export const getOrders = async () => {
  const res = await api.get("/orders");
  return res.data;
};

export const addToCart = async ({ clothingId, userId }) => {
  const res = await api.post(
    "/cart/add",
    { id_clothing: clothingId, quantity: 1 },
    { params: { user_id: userId } },
  );
  return res.data;
};
