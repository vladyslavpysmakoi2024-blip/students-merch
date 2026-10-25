import React, { Suspense, lazy, useEffect } from "react";
import {
  Routes,
  Route,
  Navigate,
  useLocation,
  useNavigationType,
} from "react-router-dom";

import Header from "@components/Header";
import Footer from "@components/Footer";
import "@/App.css";

import Home from "@pages/Home";
import ProfilePage from "@pages/ProfilePage";
import SearchPage from "@pages/SearchPage";
import ProductPage from "@pages/ProductPage";
import LoginPage from "@pages/LoginPage";
import Registration from "@components/Registration";
import CartPage from "@pages/CartPage";
import FavoritesPage from "@pages/FavoritesPage";
import CheckoutPage from "@pages/CheckoutPage";
import SurveyPage from "@pages/SurveyPage";
import SurveyRewardPage from "@pages/SurveyRewardPage";

import { ProtectedRoute } from "@features/auth/ProtectedRoute";

const ModelPage = lazy(() => import("@pages/ModelPage"));
const AdminPage = lazy(() => import("@pages/AdminPage"));

function App() {
  const { pathname, search } = useLocation();
  const navigationType = useNavigationType();

  useEffect(() => {
    if (navigationType !== "POP") {
      window.scrollTo({ top: 0, left: 0, behavior: "instant" });
    }
  }, [pathname, search, navigationType]);

  if (pathname.startsWith("/officemanager")) {
    return (
      <Suspense fallback={<div className="admin-page">Завантаження...</div>}>
        <AdminPage />
      </Suspense>
    );
  }

  return (
    <div className="app">
      <Header />

      <Suspense
        fallback={
          <div
            style={{
              padding: "50px",
              textAlign: "center",
              color: "#ffffff",
              fontSize: "18px",
            }}
          >
            Завантаження...
          </div>
        }
      >
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/search" element={<SearchPage />} />
          <Route path="/product" element={<ProductPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/registration" element={<Registration />} />
          <Route path="/checkout" element={<CheckoutPage />} />
          <Route path="/model" element={<ModelPage />} />
          <Route
            path="/survey"
            element={
              <ProtectedRoute>
                <SurveyPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/survey/reward"
            element={
              <ProtectedRoute>
                <SurveyRewardPage />
              </ProtectedRoute>
            }
          />

          <Route
            path="/favorites"
            element={
              <ProtectedRoute>
                <FavoritesPage />
              </ProtectedRoute>
            }
          />

          <Route
            path="/cart"
            element={
              <ProtectedRoute>
                <CartPage />
              </ProtectedRoute>
            }
          />

          <Route
            path="/me"
            element={
              <ProtectedRoute>
                <ProfilePage />
              </ProtectedRoute>
            }
          />

          <Route path="*" element={<Navigate to="/" />} />
        </Routes>
      </Suspense>

      <Footer />
    </div>
  );
}

export default App;
