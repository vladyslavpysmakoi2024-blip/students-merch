import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import ProductGrid from "./ProductGrid";
import { useMySurvey } from "../features/survey/useSurvey";
import { useAddPackageToCart } from "../features/cart/useCart";
import { findPackageById } from "../features/survey/packages";
import { clothingPhotoSrc } from "../shared/lib/clothingPhoto";
import { api } from "../shared/api/instance";

function CatalogSection() {
  const navigate = useNavigate();
  const { survey } = useMySurvey();
  const { mutate: addPackageToCart, isPending: isAddingToCart } =
    useAddPackageToCart();
  const [cartSuccess, setCartSuccess] = useState(false);
  const [products, setProducts] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isError, setIsError] = useState(false);

  const assignedPackage =
    survey?.package ||
    (survey?.assigned_package_id && findPackageById(survey.assigned_package_id));
  const isConfirmed = Boolean(survey?.is_package_confirmed);

  const groupedProducts = products.reduce((acc, val) => {
    const key = val.type;
    if (!acc[key]) {
      acc[key] = [];
    }
    acc[key].push(val);
    return acc;
  }, {});

  useEffect(() => {
    const setData = async () => {
      try {
        const response = await api.get("/clothing/simple-list");
        const data = response.data;
        setProducts(data);
      } catch (ex) {
        console.log(`Error fetching clothing: ${ex}`);
        setIsError(true);
      } finally {
        setIsLoading(false);
      }
    };
    setData();
  }, []);

  if (isLoading) {
    return (
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
    );
  }

  if (isError) {
    return (
      <div className="product-list-state">Не вдалося завантажити товари.</div>
    );
  }

  const teePhoto =
    assignedPackage?.tshirt &&
    (clothingPhotoSrc(assignedPackage.tshirt) || assignedPackage.tshirt.photo);
  const totePhoto =
    assignedPackage?.tote &&
    (clothingPhotoSrc(assignedPackage.tote) || assignedPackage.tote.photo);

  const handleAddToCart = () => {
    if (!assignedPackage) return;
    addPackageToCart(
      {
        packageId: assignedPackage.id,
        tshirtId: assignedPackage.tshirt.id,
        toteId: assignedPackage.tote.id,
      },
      {
        onSuccess: () => {
          setCartSuccess(true);
          setTimeout(() => setCartSuccess(false), 3000);
        },
        onError: () => {
          alert("Не вдалося додати сет у кошик.");
        },
      },
    );
  };

  return (
    <section className="catalog">
      <div className="catalog-title-wrapper">
        <h2 className="catalog-title">КАТАЛОГ</h2>
      </div>

      {assignedPackage && (
        <div className="catalog-assigned-section">
          <div className="catalog-assigned-header">
            <h3 className="catalog-assigned-title">
              <span>✨ Твій персональний сет</span>
              <span className="catalog-assigned-pill">−{assignedPackage.discountPercent}% ЗНИЖКА</span>
            </h3>
            <span className="survey-package-highlight-tag">
              {isConfirmed ? "🔒 ЗАКРІПЛЕНО ЗА ПРОФІЛЕМ" : "🎲 ПРИЗНАЧЕНИЙ ОБРАЗ"}
            </span>
          </div>

          <div className="catalog-assigned-card">
            <div style={{ display: "flex", alignItems: "center", gap: "16px", flexWrap: "wrap" }}>
              {(teePhoto || totePhoto) && (
                <div style={{ display: "flex", gap: "8px" }}>
                  {teePhoto && (
                    <div
                      style={{
                        width: "60px",
                        height: "60px",
                        borderRadius: "12px",
                        backgroundImage: `url(${teePhoto})`,
                        backgroundSize: "cover",
                        backgroundPosition: "center",
                        border: "1px solid rgba(61, 86, 144, 0.15)",
                      }}
                    />
                  )}
                  {totePhoto && (
                    <div
                      style={{
                        width: "60px",
                        height: "60px",
                        borderRadius: "12px",
                        backgroundImage: `url(${totePhoto})`,
                        backgroundSize: "cover",
                        backgroundPosition: "center",
                        border: "1px solid rgba(61, 86, 144, 0.15)",
                      }}
                    />
                  )}
                </div>
              )}

              <div className="catalog-assigned-details">
                <h4 className="catalog-assigned-name">
                  {assignedPackage.tshirt.name} + {assignedPackage.tote.name}
                </h4>
                <p className="catalog-assigned-meta">
                  Кольори: {assignedPackage.tshirt.color} · {assignedPackage.tote.color}
                </p>
                <div className="catalog-assigned-pricing">
                  <span className="catalog-assigned-price-old">
                    {assignedPackage.price} грн
                  </span>
                  <span className="catalog-assigned-price-new">
                    {assignedPackage.discountedPrice} грн
                  </span>
                </div>
              </div>
            </div>

            <div className="catalog-assigned-action" style={{ display: "flex", gap: "10px", flexWrap: "wrap" }}>
              <button
                type="button"
                className="profile-action-btn"
                onClick={handleAddToCart}
                disabled={isAddingToCart}
              >
                {isAddingToCart
                  ? "ДОДАВАННЯ..."
                  : cartSuccess
                  ? "ДОДАНО! 🎉"
                  : "ДОДАТИ В КОШИК 🛍️"}
              </button>

              <button
                type="button"
                className="profile-secondary-outline-btn"
                onClick={() => navigate("/survey/reward")}
              >
                ПЕРЕГЛЯНУТИ СЕТИ
              </button>
            </div>
          </div>
        </div>
      )}

      {Object.entries(groupedProducts).map(([ctg, arr]) => (
        <ProductGrid key={ctg} ctg={ctg} items={arr} />
      ))}

      {products.length === 0 && (
        <div className="product-list-state">Наразі товарів немає.</div>
      )}
    </section>
  );
}

export default CatalogSection;
