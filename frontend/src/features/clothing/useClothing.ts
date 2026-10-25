import { useQuery } from "@tanstack/react-query";
import {
  filterClothing,
  getClothingDetail,
  getColoredVariants,
  getSimpleList,
  searchClothing,
} from "@features/clothing/api";
import { ClothingItem } from "@shared/types/api";

export const clothingKeys = {
  all: ["clothing"] as const,
  list: () => [...clothingKeys.all, "list"] as const,
  search: (params: Record<string, unknown>) =>
    [...clothingKeys.all, "search", params] as const,
  liveSearch: (query: string) => [...clothingKeys.all, "live", query] as const,
  detail: (id?: string | number | null) =>
    [...clothingKeys.all, "detail", id] as const,
  variants: (name?: string | null, color?: string | null) =>
    [...clothingKeys.all, "variants", name, color] as const,
};

export const useClothingList = () => {
  const { data, isLoading, isError } = useQuery({
    queryKey: clothingKeys.list(),
    queryFn: getSimpleList,
    staleTime: 5 * 60 * 1000,
  });

  return {
    clothes: Array.isArray(data) ? data : ([] as ClothingItem[]),
    isLoading,
    isError,
  };
};

export interface ClothingSearchHookParams {
  query?: string;
  clothingType?: string;
  color?: string;
  size?: string;
  minPrice?: string;
  maxPrice?: string;
}

export const useClothingSearch = ({
  query,
  clothingType,
  color,
  size,
  minPrice,
  maxPrice,
}: ClothingSearchHookParams) => {
  const isFiltering = Boolean(
    clothingType || color || size || minPrice || maxPrice,
  );

  const { data, isLoading, isError } = useQuery({
    queryKey: clothingKeys.search({
      query,
      clothingType,
      color,
      size,
      minPrice,
      maxPrice,
    }),
    queryFn: () => {
      if (isFiltering) {
        return filterClothing({
          clothing_type: clothingType || undefined,
          color: color || undefined,
          size: size || undefined,
          min_price: minPrice || undefined,
          max_price: maxPrice || undefined,
        });
      }
      if (query) {
        return searchClothing(query);
      }
      return getSimpleList();
    },
    staleTime: 30_000,
  });

  return {
    results: Array.isArray(data) ? data : ([] as ClothingItem[]),
    loading: isLoading,
    isError,
    isFiltering,
  };
};

export const useLiveSearch = (query: string) => {
  const trimmed = query?.trim() || "";

  const { data, isLoading } = useQuery({
    queryKey: clothingKeys.liveSearch(trimmed),
    queryFn: () => searchClothing(trimmed),
    enabled: trimmed.length > 0,
    staleTime: 30_000,
  });

  const rawData = Array.isArray(data) ? data : [];

  return {
    searchResults: rawData.slice(0, 3),
    isLoading,
  };
};

export const useClothingDetail = (id?: string | null) => {
  const { data, isLoading, isError } = useQuery({
    queryKey: clothingKeys.detail(id),
    queryFn: () => getClothingDetail(id as string),
    enabled: Boolean(id),
    staleTime: 5 * 60 * 1000,
  });

  return {
    product: data,
    isLoading,
    isError,
  };
};

export const useClothingVariants = (
  name?: string | null,
  color?: string | null,
) => {
  const { data } = useQuery({
    queryKey: clothingKeys.variants(name, color),
    queryFn: () => getColoredVariants({ name, color }),
    enabled: Boolean(name && color),
    staleTime: 60 * 1000,
  });

  return { variants: Array.isArray(data) ? data : ([] as ClothingItem[]) };
};
