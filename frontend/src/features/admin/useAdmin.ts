import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  createClothes,
  createPromo,
  deleteClothes,
  deletePromo,
  getAdminClothing,
  getAdminOrders,
  getAdminPromos,
  updateClothes,
  updateClothing,
  updatePromo,
  uploadClothingPhoto,
} from "@features/admin/api";
import { clothingKeys } from "@features/clothing/useClothing";

export const adminKeys = {
  clothing: ["admin", "clothing"] as const,
  promos: ["admin", "promos"] as const,
  orders: ["admin", "orders"] as const,
  photoUpload: ["admin", "photo-upload"] as const,
};

export const useAdminClothing = () => {
  const {
    data = [],
    isLoading,
    isError,
  } = useQuery({
    queryKey: adminKeys.clothing,
    queryFn: getAdminClothing,
  });

  return { clothes: data, isLoading, isError };
};

export const useUpdateClothing = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: updateClothing,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: adminKeys.clothing });
      queryClient.invalidateQueries({ queryKey: clothingKeys.all });
    },
  });
};

export const useCreateClothes = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: createClothes,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: adminKeys.clothing });
      queryClient.invalidateQueries({ queryKey: clothingKeys.all });
    },
  });
};

export const useBulkUpdateClothes = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: updateClothes,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: adminKeys.clothing });
      queryClient.invalidateQueries({ queryKey: clothingKeys.all });
    },
  });
};

export const useDeleteClothes = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: deleteClothes,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: adminKeys.clothing });
      queryClient.invalidateQueries({ queryKey: clothingKeys.all });
    },
  });
};

export const useUploadClothingPhoto = () =>
  useMutation({
    mutationKey: adminKeys.photoUpload,
    mutationFn: uploadClothingPhoto,
  });

export const useAdminPromos = () => {
  const {
    data = [],
    isLoading,
    isError,
  } = useQuery({
    queryKey: adminKeys.promos,
    queryFn: getAdminPromos,
  });

  return { promos: data, isLoading, isError };
};

export const useSavePromo = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      id,
      data,
    }: {
      id: number | null;
      data: Record<string, unknown>;
    }) => (id ? updatePromo({ id, data }) : createPromo(data)),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: adminKeys.promos });
    },
  });
};

export const useDeletePromo = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: deletePromo,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: adminKeys.promos });
    },
  });
};

export const useAdminOrders = () => {
  const {
    data = [],
    isLoading,
    isError,
  } = useQuery({
    queryKey: adminKeys.orders,
    queryFn: getAdminOrders,
  });

  return { orders: data, isLoading, isError };
};
