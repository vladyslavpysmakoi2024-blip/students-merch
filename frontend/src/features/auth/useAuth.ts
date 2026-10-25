import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  getCurrentUser,
  login as loginApi,
  logout as logoutApi,
  register as registerApi,
  updateUser as updateUserApi,
  updateAvatar as updateAvatarApi,
  deleteAvatar as deleteAvatarApi,
  updatePassword as updatePasswordApi,
  LoginPayload,
  RegisterPayload,
  UpdateUserPayload,
  UpdatePasswordPayload,
} from "@features/auth/api";

const authKeys = {
  user: ["user", "me"] as const,
};

export const useCurrentUser = () => {
  const {
    data: user,
    isLoading,
    isError,
  } = useQuery({
    queryFn: getCurrentUser,
    queryKey: authKeys.user,
    retry: false,
    staleTime: 5 * 60 * 1000,
  });

  return { user, isLoading, isError, isLoggedIn: !!user };
};

export const useLogin = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: LoginPayload) => loginApi(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: authKeys.user });
    },
  });
};

export const useRegister = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: RegisterPayload) => registerApi(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: authKeys.user });
    },
  });
};

export const useLogout = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: logoutApi,
    onSuccess: () => {
      queryClient.setQueryData(authKeys.user, null);
      queryClient.removeQueries({ queryKey: authKeys.user });
    },
  });
};

export const useUpdateUser = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: UpdateUserPayload) => updateUserApi(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: authKeys.user });
    },
  });
};

export const useUpdateAvatar = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (file: File) => updateAvatarApi(file),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: authKeys.user });
    },
  });
};

export const useDeleteAvatar = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: deleteAvatarApi,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: authKeys.user });
    },
  });
};

export const useUpdatePassword = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: UpdatePasswordPayload) => updatePasswordApi(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: authKeys.user });
    },
  });
};
