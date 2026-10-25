import { api } from "@shared/api/instance";
import { ClothingItem } from "@shared/types/api";

export interface ClothingFilterParams {
  clothing_type?: string;
  color?: string;
  size?: string;
  min_price?: string | number;
  max_price?: string | number;
}

export const getSimpleList = async (): Promise<ClothingItem[]> => {
  const res = await api.get<ClothingItem[]>("clothing/simple-list");
  return res.data;
};

export const searchClothing = async (title: string): Promise<ClothingItem[]> => {
  const res = await api.get<ClothingItem[]>("clothing/search", {
    params: { title },
  });
  return res.data;
};

export const filterClothing = async (
  params: ClothingFilterParams,
): Promise<ClothingItem[]> => {
  const res = await api.get<ClothingItem[]>("clothing/filter", { params });
  return res.data;
};

export const getColoredVariants = async ({
  name,
  color,
}: {
  name?: string | null;
  color?: string | null;
}): Promise<ClothingItem[]> => {
  const res = await api.get<ClothingItem[]>("clothing/colored", {
    params: { clname: name, clcolor: color },
  });
  return res.data;
};

export const getClothingDetail = async (
  id: string | number,
): Promise<ClothingItem> => {
  const res = await api.get<ClothingItem>(`clothing/${id}`);
  return res.data;
};
