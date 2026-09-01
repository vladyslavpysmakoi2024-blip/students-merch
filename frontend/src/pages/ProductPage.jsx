import React, { Suspense, useState, useEffect } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { useCurrentUser } from "../features/auth/useAuth";
import { api } from "../shared/api/instance";
import { useAddFavorite, useFavorites, useRemoveFavorite } from "../features/profile/useProfile";

import { Canvas } from "@react-three/fiber";
import { OrbitControls, Center, Environment } from "@react-three/drei";
import Model3dCharacter from "../components/Model3dCharacter";

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
  const [heartAnim, setHeartAnim] = useState(false);
  const [isFavoriteLocal, setIsFavoriteLocal] = useState(false);

  // Доступні розміри для вибору
  const sizes = ["XS", "S", "M", "L", "XL", "XXL"];

  const { favorites } = useFavorites(isLoggedIn);
  const { mutate: addFav } = useAddFavorite();
  const { mutate: removeFav } = useRemoveFavorite();

  // Перевіряємо, чи є поточний товар у списку вподобань
  const isFavoriteFromApi = favorites?.some((fav) => fav.clothing?.id === product?.id);
  const isFavorite = isFavoriteLocal || isFavoriteFromApi;

  const handleFavoriteToggle = () => {
    if (!isLoggedIn) {
      navigate("/login");
      return;
    }

    // Миттєво перемикаємо локальний стан (для відображення)
    setIsFavoriteLocal((prev) => !prev);

    // Запускаємо анімацію
    setHeartAnim(false);
    requestAnimationFrame(() => {
      requestAnimationFrame(() => setHeartAnim(true));
    });
    setTimeout(() => setHeartAnim(false), 400);

    if (isFavorite) {
      removeFav(product.id);
    } else {
      addFav(product.id);
    }
  };

  // Отримання даних про одяг
  useEffect(() => {
    if (!id) {
      setProduct(mockProduct);
      return;
    }

    api
      .get(`/clothing/${id}`)
      .then((res) => setProduct(res.data))
      .catch((err) => {
        console.error("Товар не знайдено, використовуємо демо-товар:", err);
        setProduct(mockProduct);
      });
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
            <button
              className={`favorite-badge-btn${heartAnim ? " heart-pop" : ""}`}
              onClick={handleFavoriteToggle}
              aria-label="Додати в обране"
              title="Додати в обране"
            >
              <svg
                width="22"
                height="22"
                viewBox="0 0 24 24"
                fill={isFavorite ? "#F23535" : "none"}
                stroke={isFavorite ? "#F23535" : "#3D5690"}
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <path d="M12 21C12 21 1 14.5 1 8.5C1 5.42 3.42 3 6.5 3C8.24 3 10.09 3.81 12 5.08C13.91 3.81 15.76 3 17.5 3C20.58 3 23 5.42 23 8.5C23 14.5 12 21 12 21Z" />
              </svg>
            </button>
            <img src="hoodie.png" alt={product.name} />
          </div>

          <div className="thumbnail-list">
            <div className="thumbnail-card"></div>
            <div className="thumbnail-card"></div>
            <div className="thumbnail-card"></div>
          </div>
        </div>

        <div className="product-info-column">
          <div className="product-details">
            <div className="info-section">
              <h2 className="product-title" style={{ marginBottom: "15px" }}>{product.name}</h2>

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

          <div className="bottom-gallery">
            <div className="gallery-card"></div>
            <div className="gallery-card"></div>
            <div className="gallery-card"></div>
            <div className="gallery-card"></div>
          </div>
        </div>

        {/* Поки тут модель як заглушку поставив. Хто робить цю сторінку поміняйте стилі і переставте це plzzz */}
      <div className="model-card">
        <div id="model-container" >
          <Canvas 
          camera={{ position: [0, 2, 5], fov: 45 }}>
            <ambientLight intensity={0.7}/>
            <directionalLight position={[5, 5, 5]} intensity={1.2}/>

            <Suspense fallback={null}>
              <Center>
                <Model3dCharacter clothingType={"Футболка"} />
              </Center>
              <Environment preset="city" />
            </Suspense>

            <OrbitControls 
            minDistance={6.5} 
            maxDistance={10} 
            makeDefault
            autoRotate
            autoRotateSpeed={1.5} />
          </Canvas>
        </div>
      </div>
      </div>
    </main>
  );
}

export default ProductPage;
