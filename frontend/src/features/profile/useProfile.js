import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  addFavorite,
  addToCart,
  getFavorites,
  getOrderDetail,
  getOrderReceipt,
  getOrders,
  removeFavorite,
} from "./api";

export const profileKeys = {
  favorites: ["favorites"],
  orders: ["orders"],
  cart: ["cart"],
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

export const useOrderDetail = (orderId, enabled = false) => {
  const { data, isLoading, isError } = useQuery({
    queryKey: ["order_detail", orderId],
    queryFn: () => getOrderDetail(orderId),
    enabled: Boolean(enabled && orderId),
  });

  return { order: data, isLoading, isError };
};

export const useOrderReceipt = (orderId, enabled = false) => {
  const { data, isLoading, isError, error } = useQuery({
    queryKey: ["order_receipt", orderId],
    queryFn: () => getOrderReceipt(orderId),
    enabled: Boolean(enabled && orderId),
  });

  return { receipt: data, isLoading, isError, error };
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
