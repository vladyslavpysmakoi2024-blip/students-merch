import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  getCurrentUser,
  login as loginApi,
  logout as logoutApi,
  register as registerApi,
  updateUser as updateUserApi,
  updatePassword as updatePasswordApi,
} from "./api";

const authKeys = {
  user: ["user", "me"],
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
    mutationFn: (data) => loginApi(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: authKeys.user });
    },
  });
};

export const useRegister = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data) => registerApi(data),
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
      queryClient.invalidateQueries({ queryKey: authKeys.user });
    },
  });
};

export const useUpdateUser = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data) => updateUserApi(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: authKeys.user });
    },
  });
};
export const useUpdatePassword = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data) => updatePasswordApi(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: authKeys.user });
    },
  });
};
