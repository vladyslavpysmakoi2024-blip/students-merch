import { useQuery } from "@tanstack/react-query";
import {
  filterClothing,
  getClothingDetail,
  getSimpleList,
  searchClothing,
} from "./api";

export const clothingKeys = {
  all: ["clothing"],
  list: () => [...clothingKeys.all, "list"],
  search: (params) => [...clothingKeys.all, "search", params],
  liveSearch: (query) => [...clothingKeys.all, "live", query],
  detail: (id) => [...clothingKeys.all, "detail", id],
};

export const useClothingSearch = ({
  query,
  clothingType,
  color,
  size,
  minPrice,
  maxPrice,
}) => {
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
    results: Array.isArray(data) ? data : [],
    loading: isLoading,
    isError,
    isFiltering,
  };
};

export const useLiveSearch = (query) => {
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

export const useClothingDetail = (id) => {
  const { data, isLoading, isError } = useQuery({
    queryKey: clothingKeys.detail(id),
    queryFn: () => getClothingDetail(id),
    enabled: Boolean(id),
    staleTime: 5 * 60 * 1000,
  });

  return {
    product: data,
    isLoading,
    isError,
  };
};
