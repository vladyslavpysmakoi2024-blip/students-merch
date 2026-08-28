import { api } from "../../shared/api/instance";

export const login = async (data) => {
  const res = await api.post("/login", data);
  return res.data;
};
export const register = async (data) => {
  const res = await api.post("/register", data);
  console.log(res.data);
  return res.data;
};
export const getCurrentUser = async (data) => {
  const res = await api.get("/users/me");
  return res.data;
};

export const logout = async () => {
  const res = await api.post("/logout");
  return res.data;
};
export const updateUser = async (data) => {
  const res = await api.patch("/users/me", data);
  return res.data;
};
export const updatePassword = async (data) => {
  const res = await api.patch("users/me/password", data);
  return res.data;
};
export const refresh = async () => {
  const res = await api.post("/refresh");
  return res.data;
};
