import { api } from "@shared/api/instance";
import { SurveyAnswer, SurveyResponseData } from "@shared/types/api";

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
