import { api } from "../../shared/api/instance";

export const getSimpleList = async () => {
  const res = await api.get("clothing/simple-list");
  return res.data;
};

export const searchClothing = async (title) => {
  const res = await api.get("clothing/search", { params: { title } });
  return res.data;
};

export const filterClothing = async (params) => {
  const res = await api.get("clothing/filter", { params });
  return res.data;
};

export const getColoredVariants = async ({ name, color }) => {
  const res = await api.get("clothing/colored", {
    params: { clname: name, clcolor: color },
  });
  return res.data;
};

export const getClothingDetail = async (id) => {
  const res = await api.get(`clothing/${id}`);
  return res.data;
};
