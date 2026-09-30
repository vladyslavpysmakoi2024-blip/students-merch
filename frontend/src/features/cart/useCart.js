import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  getCart,
  updateCartItemQuantity,
  removeCartItem,
  applyPromoCode,
  addPackageToCart,
} from "./api";

// Той самий ключ, що й profileKeys.cart у features/profile/useProfile.js,
// щоб додавання товару в кошик з інших сторінок теж оновлювало цю сторінку
export const cartKeys = {
  all: ["cart"],
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

export const useAddPackageToCart = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: addPackageToCart,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: cartKeys.all });
    },
  });
};
