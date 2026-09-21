import { api } from "../../shared/api/instance";

export const getMySurvey = async () => {
  const res = await api.get("/survey/me");
  return res.data;
};

export const submitSurvey = async (data) => {
  const res = await api.post("/survey/me", data);
  return res.data;
};
