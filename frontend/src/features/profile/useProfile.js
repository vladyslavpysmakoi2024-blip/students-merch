import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { addToCart, getFavorites, getOrders } from "./api";

export const profileKeys = {
  favorites: ["favorites"],
  orders: ["orders"],
};

export const useFavorites = () => {
  const { data = [], isLoading, isError } = useQuery({
    queryKey: profileKeys.favorites,
    queryFn: getFavorites,
  });

  return { favorites: data, isLoading, isError };
};

export const useOrders = () => {
  const { data = [], isLoading, isError } = useQuery({
    queryKey: profileKeys.orders,
    queryFn: getOrders,
  });

  return { orders: data, isLoading, isError };
};

export const useAddToCart = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: addToCart,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["cart"] });
    },
  });
};
