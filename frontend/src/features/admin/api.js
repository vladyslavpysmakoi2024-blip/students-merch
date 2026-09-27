import { api } from "../../shared/api/instance";

export const getAdminClothing = async () => {
  const res = await api.get("/admin/clothing");
  return res.data;
};

export const createClothes = async (items) => {
  const res = await api.post("/admin/clothing/bulk", { items });
  return res.data;
};

export const updateClothes = async (data) => {
  const res = await api.patch("/admin/clothing/bulk", data);
  return res.data;
};

export const deleteClothes = async (ids) => {
  const res = await api.post("/admin/clothing/bulk-delete", { ids });
  return res.data;
};

export const updateClothing = async ({ id, data }) => {
  const res = await api.put(`/admin/clothing/${id}`, data);
  return res.data;
};

export const uploadClothingPhoto = async (file) => {
  const formData = new FormData();
  formData.append("file", file);
  const res = await api.post("/admin/clothing/photo", formData);
  return res.data;
};

export const getAdminPromos = async () => {
  const res = await api.get("/admin/promo");
  return res.data;
};

export const createPromo = async (data) => {
  const res = await api.post("/admin/promo", data);
  return res.data;
};

export const updatePromo = async ({ id, data }) => {
  const res = await api.put(`/admin/promo/${id}`, data);
  return res.data;
};

export const deletePromo = async (id) => {
  const res = await api.delete(`/admin/promo/${id}`);
  return res.data;
};

export const getAdminOrders = async () => {
  const res = await api.get("/admin/orders");
  return res.data;
};
