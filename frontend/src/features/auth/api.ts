import { api } from "@shared/api/instance";
import { User } from "@shared/types/api";

export interface LoginPayload {
  email: string;
  password: string;
}

export interface RegisterPayload {
  first_name: string;
  last_name: string;
  phone_number: string;
  email: string;
  password: string;
}

export interface UpdateUserPayload {
  first_name: string;
  last_name: string;
  email: string;
  phone_number: string;
}

export interface UpdatePasswordPayload {
  current_password: string;
  new_password: string;
}

export const login = async (data: LoginPayload) => {
  const res = await api.post("/auth/login", data);
  return res.data;
};

export const register = async (data: RegisterPayload) => {
  const res = await api.post("/auth/register", data);
  return res.data;
};

export const getCurrentUser = async (): Promise<User> => {
  const res = await api.get<User>("/user/me");
  return res.data;
};

export const logout = async () => {
  const res = await api.post("/auth/logout");
  return res.data;
};

export const updateUser = async (data: UpdateUserPayload): Promise<User> => {
  const res = await api.patch<User>("/user/me", data);
  return res.data;
};

export const updateAvatar = async (file: File): Promise<User> => {
  const formData = new FormData();
  formData.append("file", file);
  const res = await api.post<User>("/user/me/avatar", formData);
  return res.data;
};

export const deleteAvatar = async (): Promise<User> => {
  const res = await api.delete<User>("/user/me/avatar");
  return res.data;
};

export const updatePassword = async (data: UpdatePasswordPayload) => {
  const res = await api.patch("/user/me/password", data);
  return res.data;
};

export const refresh = async () => {
  const res = await api.post("/auth/refresh");
  return res.data;
};
