import { api } from "@shared/api/instance";
import {
  SurveyAnswer,
  SurveyPackageItem,
  SurveyResponseData,
} from "@shared/types/api";

export const getMySurvey = async (): Promise<SurveyResponseData> => {
  const res = await api.get<SurveyResponseData>("/survey/me");
  return res.data;
};

export const submitSurvey = async (data: {
  answers: SurveyAnswer[];
}): Promise<SurveyResponseData> => {
  const res = await api.post<SurveyResponseData>("/survey/me", data);
  return res.data;
};

export const claimPackage = async (packageId?: string | null) => {
  const res = await api.post(
    "/survey/claim-package",
    packageId ? { package_id: packageId } : {},
  );
  return res.data;
};

export const getSurveyPackages = async (): Promise<SurveyPackageItem[]> => {
  const res = await api.get<SurveyPackageItem[]>("/survey/packages");
  return res.data;
};
