import { useQuery } from "@tanstack/react-query";
import { getClothingById, getClothingList } from "./api";

const clothingKeys = {
  list: ["clothing", "list"],
  detail: (id) => ["clothing", "detail", id],
};

export const useClothingList = () => {
  const {
    data: clothes = [],
    isLoading,
    isError,
  } = useQuery({
    queryFn: getClothingList,
    queryKey: clothingKeys.list,
  });

  return { clothes, isLoading, isError };
};

export const useClothingDetail = (id) => {
  const {
    data: clothing,
    isLoading,
    isError,
  } = useQuery({
    queryFn: () => getClothingById(id),
    queryKey: clothingKeys.detail(id),
    enabled: !!id,
  });

  return { clothing, isLoading, isError };
};
