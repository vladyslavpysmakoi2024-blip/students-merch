import React from "react";
import { Navigate } from "react-router-dom";
import { useCurrentUser } from "@features/auth/useAuth";

export const ProtectedRoute = ({
  children,
}: {
  children: React.ReactElement;
}) => {
  const { user, isLoading, isError } = useCurrentUser();
  if (isLoading) return <div>Завантаження...</div>;

  if (isError || !user) {
    return <Navigate to="/login" replace />;
  }

  return children;
};
