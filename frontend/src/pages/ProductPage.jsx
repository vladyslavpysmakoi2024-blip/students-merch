import React, { useState, useEffect } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { useCurrentUser } from "../features/auth/useAuth";
import { api } from "../shared/api/instance";
import { useAddFavorite, useFavorites, useRemoveFavorite } from "../features/profile/useProfile";
// Якщо ти вже виніс запити за моєю попередньою порадою,
// заміни імпорт api на: import { getProductById } from '../entities/Product/api/productApi';
export const mockProduct = {
  id: "101",
  name: "Оверсайз Худі НУЛП",
  composition: "80% Бавовна, 20% Поліестер",
  type: "Худі",
  color: "Темно-синій",
  price: 1450,
  photo: null, // Або можна вставити коротку base64 строку для тестування рендеру картинки
};
function ProductPage() {
  const [searchParams] = useSearchParams();
  const id = searchParams.get("id");
  const navigate = useNavigate();
  const { isLoggedIn } = useCurrentUser();

  const [product, setProduct] = useState();
  const [selectedSize, setSelectedSize] = useState(null);

  // Доступні розміри для вибору
  const sizes = ["XS", "S", "M", "L", "XL", "XXL"];

  const { favorites } = useFavorites();
  const { mutate: addFav } = useAddFavorite();
  const { mutate: removeFav } = useRemoveFavorite();

  // Перевіряємо, чи є поточний товар у списку вподобань
  const isFavorite = favorites?.some((fav) => fav.clothing?.id === product?.id);

  const handleFavoriteToggle = () => {
    if (!isLoggedIn) {
      navigate("/login");
      return;
    }

    if (isFavorite) {
      removeFav(product.id);
    } else {
      addFav(product.id);
    }
  };

  // Отримання даних про одяг
    useEffect(() => {
      api
        .get(`/clothing/${id}`) // Або getProductById(id)
        .then((res) => setProduct(res.data))
        .catch((err) => console.error("Товар не знайдено:", err));
    }, [id]);

  // Стилізація фону сторінки (з гілки колеги)
  useEffect(() => {
    document.body.classList.add("product-page-body");
    return () => {
      document.body.classList.remove("product-page-body");
    };
  }, []);

  const handleBuyClick = () => {
    if (!isLoggedIn) {
      navigate("/login");
    } else if (!selectedSize) {
      // Додано перевірку, щоб користувач не забув обрати розмір
      alert("Будь ласка, оберіть розмір перед додаванням у кошик!");
    } else {
      alert("Товар додано в кошик!");
    }
  };

  if (!product) {
    return (
      <div
        style={{
          padding: "50px",
          textAlign: "center",
          color: "#3D5690",
          fontSize: "18px",
        }}
      >
        Завантаження...
      </div>
    );
  }

  return (
    <main className="product-page container">
      <div className="product-main-content">
        <div className="product-visuals">
          <div className="product-image-card">
            {/* Якщо фото у base64, можна виводити так: src={`data:image/jpeg;base64,${product.photo}`} */}
            <img src="hoodie.png" alt={product.name} />
          </div>
        </div>

        <div className="">
          <div className="product-details">
            <div className="info-section">
              {/* Обгортка для сердечка та назви */}
              <div style={{ display: "flex", alignItems: "center", gap: "15px", marginBottom: "15px" }}>
                <svg
                  onClick={handleFavoriteToggle}
                  width="35"
                  height="35"
                  viewBox="0 0 24 24"
                  fill={isFavorite ? "#F23535" : "#b0b0b0"}
                  style={{ cursor: "pointer", transition: "fill 0.2s ease-in-out", flexShrink: 0 }}
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z" />
                </svg>

                <h2 className="product-title" style={{ margin: 0 }}>{product.name}</h2>
              </div>

              <p className="material-info">
                СКЛАД: {product.composition || "БАВОВНА 100%"}
              </p>
              <p className="material-info">ТИП: {product.type}</p>
              <p className="material-info">КОЛІР: {product.color}</p>
            </div>

            <div className="purchase-controls">
              <div className="price-tag">ЦІНА: {product.price} ₴</div>
              <button className="buy-btn" onClick={handleBuyClick}>
                КУПИТИ
              </button>

              <div className="size-selector">
                {sizes.map((size) => (
                  <button
                    key={size}
                    className={`size-chip ${selectedSize === size ? "active" : ""}`}
                    onClick={() => setSelectedSize(size)}
                    // Додано базові стилі для активного стану, якщо їх ще немає в CSS
                    style={{
                      background: selectedSize === size ? "#8AB1C7" : "",
                      color: selectedSize === size ? "#FDFDF5" : "",
                      cursor: "pointer",
                      border: "none",
                    }}
                  >
                    {size}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}

export default ProductPage;
