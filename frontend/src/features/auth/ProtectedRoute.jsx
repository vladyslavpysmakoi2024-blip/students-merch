import { useCurrentUser } from "./useAuth";
import { Navigate } from "react-router-dom";
export const ProtectedRoute = ({ children }) => {
  const { user, isLoading, isError } = useCurrentUser();
  if (isLoading) return <div>Завантаження...</div>;

  if (isError || !user) {
    return <Navigate to="/login" replace />;
  }

  return children;
};
