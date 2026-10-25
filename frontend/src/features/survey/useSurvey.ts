import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { getMySurvey, submitSurvey } from "@features/survey/api";

export const surveyKeys = {
  me: ["survey", "me"] as const,
};

export const useMySurvey = () => {
  const { data, isLoading, isError, error } = useQuery({
    queryKey: surveyKeys.me,
    queryFn: getMySurvey,
    retry: false,
  });

  const status = (error as { response?: { status?: number } } | null)?.response
    ?.status;
  const notFound = status === 404;

  return {
    survey: notFound ? null : data,
    isLoading,
    isError: isError && !notFound,
  };
};

export const useSubmitSurvey = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: submitSurvey,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: surveyKeys.me });
      queryClient.invalidateQueries({ queryKey: ["user", "me"] });
    },
  });
};
