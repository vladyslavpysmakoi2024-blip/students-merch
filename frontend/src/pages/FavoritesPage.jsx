import { useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import "../App.css";

import {
  useAddToCart,
  useFavorites,
  useRemoveFavorite,
} from "../features/profile/useProfile";
import { useCurrentUser } from "../features/auth/useAuth";

import { clothingPhotoSrc } from "../shared/lib/clothingPhoto";

function FavoritesPage() {
  const navigate = useNavigate();
  const { user } = useCurrentUser();
  const { favorites, isLoading } = useFavorites();
  const { mutate: removeFav } = useRemoveFavorite();
  const { mutate: addToCart } = useAddToCart();

  useEffect(() => {
    document.body.classList.add("favorites-page-body");
    return () => {
      document.body.classList.remove("favorites-page-body");
    };
  }, []);

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

  const visibleFavorites = favorites.filter((item) => item.clothing);

  return (
    <main className="favorites-page">
      <div className="container">
        <section className="favorites-hero">
          <img
            src="/cat-thumbs-up.png"
            alt=""
            className="favorites-hero-cat"
          />
          <div className="favorites-hero-copy">
            <div className="favorites-badge">ЗБЕРЕЖЕНЕ</div>
            <h1 className="favorites-title">Речі, які гріють серце</h1>
            <p className="favorites-subtitle">
              Твій особистий куточок мерчу. Додай у кошик, коли будеш готовий(ва).
            </p>
          </div>
          <div className="favorites-count-chip">
            {isLoading ? "…" : visibleFavorites.length}
            <span>у списку</span>
          </div>
        </section>

        <section className="favorites-panel">
          {isLoading && (
            <p className="favorites-status">Завантаження...</p>
          )}

          {!isLoading && visibleFavorites.length === 0 && (
            <div className="favorites-empty">
              <div className="favorites-empty-heart">♡</div>
              <h3>Поки тут порожньо</h3>
              <p>Збережи худі чи футболку з каталогу — вони з’являться тут.</p>
              <Link to="/search" className="btn-add-cart favorites-empty-cta">
                До каталогу
              </Link>
            </div>
          )}

          {!isLoading && visibleFavorites.length > 0 && (
            <div className="favorites-list">
              {visibleFavorites.map((item) => {
                const clothing = item.clothing;
                const photoSrc = clothingPhotoSrc(clothing);
                const details = [clothing.type, clothing.color_name]
                  .filter(Boolean)
                  .join(" · ");

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
                            ? { backgroundImage: `url(${photoSrc})` }
                            : undefined
                        }
                      >
                        {!photoSrc && (
                          <span className="fav-photo-icon">♡</span>
                        )}
                        <span className="fav-heart-chip" aria-hidden="true">
                          ♥
                        </span>
                      </div>
                      <div className="fav-details">
                        <h3 className="fav-name">{clothing.name}</h3>
                        {details && (
                          <p className="fav-item-meta">{details}</p>
                        )}
                        <p className="fav-price">{clothing.price} ₴</p>
                        <span className="fav-badge">В наявності</span>
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
          )}
        </section>
      </div>
    </main>
  );
}

export default FavoritesPage;
