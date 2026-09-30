import { api } from "../../shared/api/instance";

export const getMySurvey = async () => {
  const res = await api.get("/survey/me");
  return res.data;
};

export const submitSurvey = async (data) => {
  const res = await api.post("/survey/me", data);
  return res.data;
};

export const claimPackage = async (packageId) => {
  const res = await api.post(
    "/survey/claim-package",
    packageId ? { package_id: packageId } : {},
  );
  return res.data;
};

export const getSurveyPackages = async () => {
  const res = await api.get("/survey/packages");
  return res.data;
};
