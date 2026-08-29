import { api } from "../../shared/api/instance";

export const getClothingList = async () => {
  const res = await api.get("/simple-list");
  return res.data;
};

export const getClothingById = async (id) => {
  const res = await api.get(`/clothing/${id}`);
  return res.data;
};
