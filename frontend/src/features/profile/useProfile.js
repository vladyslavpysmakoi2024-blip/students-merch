import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { addToCart, getFavorites, getOrders, removeFavorite } from "./api";
import { addFavorite } from "./api"; // додай в існуючий імпорт

export const profileKeys = {
  favorites: ["favorites"],
  orders: ["orders"],
  cart: ["cart"]
};

export const useAddFavorite = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: addFavorite,
    onSuccess: () => {
      // Одразу оновлюємо кеш, щоб товар з'явився у віш-листі
      queryClient.invalidateQueries({ queryKey: profileKeys.favorites });
    },
  });
};

export const useFavorites = (enabled = true) => {
  const { data = [], isLoading, isError } = useQuery({
    queryKey: profileKeys.favorites,
    queryFn: getFavorites,
    enabled: Boolean(enabled),
  });

  return { favorites: data, isLoading, isError };
};

export const useRemoveFavorite = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: removeFavorite,
    onSuccess: () => {
      // Оновлюємо дані після успішного видалення
      queryClient.invalidateQueries({ queryKey: profileKeys.favorites });
    },
  });
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
      queryClient.invalidateQueries({ queryKey: profileKeys.cart });
    },
  });
};