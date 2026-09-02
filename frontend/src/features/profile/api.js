import { api } from "../../shared/api/instance";

export const getFavorites = async () => {
  const res = await api.get("/favorite");
  return res.data;
};

export const addFavorite = async (clothingId) => {
  const res = await api.post("/favorite", { id_clothing: clothingId });
  return res.data;
};

export const removeFavorite = async (clothingId) => {
  const res = await api.delete(`/favorite/${clothingId}`);
  return res.data;
};

export const getOrders = async () => {
  const res = await api.get("/orders");
  return res.data;
};

export const addToCart = async ({ clothingId }) => {
  const res = await api.post("/cart", {
    id_clothing: clothingId,
    quantity: 1,
  });
  return res.data;
};
