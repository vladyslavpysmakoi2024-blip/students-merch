import { Routes, Route, Navigate } from "react-router-dom";
import Header from "./components/Header";
import Footer from "./components/Footer";
import "./App.css";

import Home from "./pages/Home";
import ProfilePage from "./pages/ProfilePage";
import SearchPage from "./pages/SearchPage";
import ProductPage from "./pages/ProductPage";
import LoginPage from "./pages/LoginPage";
import Registration from "./components/Registration";
import CartPage from "./pages/CartPage";
import FavoritesPage from "./pages/FavoritesPage";
import { ProtectedRoute } from "./features/auth/ProtectedRoute";
import ModelPage from "./pages/ModelPage";

function App() {
  return (
    <div className="app">
      <Header />

      <Routes>
        {/* Публічні маршрути */}
        <Route path="/" element={<Home />} />
        <Route path="/search" element={<SearchPage />} />
        <Route path="/product" element={<ProductPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/registration" element={<Registration />} />
        <Route path="/model" element={<ModelPage />} />

        {/* Захищені маршрути */}
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

        {/* Fallback для неіснуючих сторінок */}
        <Route path="*" element={<Navigate to="/" />} />
      </Routes>

      <Footer />
    </div>
  );
}

export default App;
