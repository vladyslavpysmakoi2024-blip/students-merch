import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  getCart,
  updateCartItemQuantity,
  removeCartItem,
  applyPromoCode,
} from "@features/cart/api";

export const cartKeys = {
  all: ["cart"] as const,
};

export const useCart = () => {
  const { data = [], isLoading, isError } = useQuery({
    queryKey: cartKeys.all,
    queryFn: getCart,
  });

  return { cart: data, isLoading, isError };
};

export const useUpdateCartItemQuantity = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: updateCartItemQuantity,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: cartKeys.all });
    },
  });
};

export const useRemoveCartItem = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: removeCartItem,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: cartKeys.all });
    },
  });
};

export const useApplyPromoCode = () => {
  return useMutation({
    mutationFn: applyPromoCode,
  });
};
