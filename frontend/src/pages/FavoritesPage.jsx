import React from "react";
import { Link, useNavigate } from "react-router-dom";
import "../App.css";

import {
  useAddToCart,
  useFavorites,
  useRemoveFavorite,
} from "../features/profile/useProfile";
import { useCurrentUser } from "../features/auth/useAuth";

function FavoritesPage() {
  const navigate = useNavigate();
  const { user } = useCurrentUser();
  const { favorites, isLoading } = useFavorites();
  const { mutate: removeFav } = useRemoveFavorite();
  const { mutate: addToCart } = useAddToCart();

  const handleAddToCart = (clothing) => {
    if (!user) {
      navigate("/login");
      return;
    }

    addToCart(
      { clothingId: clothing.id },
      {
        onSuccess: () => {
          alert(`Товар "${clothing.name}" додано в кошик.`);
        },
        onError: () => {
          alert("Помилка при додаванні в кошик.");
        },
      },
    );
  };

  const handleRemove = (clothingId) => {
    removeFav(clothingId);
  };

  return (
    <main
      className="search-page favorites-page"
      style={{ paddingTop: "50px", paddingBottom: "50px" }}
    >
      <div className="container" style={{ position: "relative" }}>
        <div className="favorites-header">
          <img
            src="/cat-thumbs-up.png"
            alt="cat thumbs up"
            className="cat-header-mascot"
          />
          <h2 className="search-title title-pill">Збережене</h2>
        </div>

        <div className="favorites-list" style={{ position: "relative", zIndex: 2 }}>
          {isLoading && <p style={{ color: "#3d5690" }}>Завантаження...</p>}

          {!isLoading && favorites.length === 0 && (
            <p style={{ color: "#3d5690" }}>
              У збереженому поки немає товарів 😢
            </p>
          )}

          {!isLoading &&
            favorites.map((item) => {
              const clothing = item.clothing;
              if (!clothing) return null;

              const photoSrc = clothing.photo
                ? clothing.photo.startsWith("data:")
                  ? clothing.photo
                  : `data:image/jpeg;base64,${clothing.photo}`
                : null;

              return (
                <div className="favorite-item-row" key={item.id}>
                  <Link
                    to={`/product?id=${clothing.id}`}
                    className="fav-item-link"
                  >
                    <div
                      className="fav-image-placeholder"
                      style={
                        photoSrc
                          ? {
                              backgroundImage: `url(${photoSrc})`,
                              backgroundSize: "cover",
                              backgroundPosition: "center",
                            }
                          : {}
                      }
                    >
                      {!photoSrc && (
                        <span className="fav-photo-icon">📷</span>
                      )}
                    </div>
                    <div className="fav-details">
                      <h3 className="fav-name">{clothing.name}</h3>
                      <p className="fav-price">{clothing.price} ₴</p>
                      <div className="fav-meta">
                        <span className="fav-badge">В наявності</span>
                      </div>
                    </div>
                  </Link>

                  <div className="fav-actions">
                    <button
                      className="btn-add-cart"
                      onClick={() => handleAddToCart(clothing)}
                    >
                      У кошик
                    </button>
                    <button
                      className="btn-remove-fav"
                      onClick={() => handleRemove(clothing.id)}
                      title="Видалити зі збереженого"
                    >
                      <svg
                        width="24"
                        height="24"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="2"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                      >
                        <line x1="18" y1="6" x2="6" y2="18"></line>
                        <line x1="6" y1="6" x2="18" y2="18"></line>
                      </svg>
                    </button>
                  </div>
                </div>
              );
            })}
        </div>
      </div>
    </main>
  );
}

export default FavoritesPage;
