import { api } from "../../shared/api/instance";

export const login = async (data) => {
  const res = await api.post("/auth/login", data);
  return res.data;
};

export const register = async (data) => {
  const res = await api.post("/auth/register", data);
  return res.data;
};

export const getCurrentUser = async () => {
  const res = await api.get("/user/me");
  return res.data;
};

export const logout = async () => {
  const res = await api.post("/auth/logout");
  return res.data;
};

export const updateUser = async (data) => {
  const res = await api.patch("/user/me", data);
  return res.data;
};

export const updatePassword = async (data) => {
  const res = await api.patch("/user/me/password", data);
  return res.data;
};

export const refresh = async () => {
  const res = await api.post("/auth/refresh");
  return res.data;
};