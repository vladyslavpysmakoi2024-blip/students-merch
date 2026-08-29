import React, { useState, useEffect } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { useCurrentUser } from "../features/auth/useAuth";
import {
  useClothingDetail,
  useClothingList,
} from "../features/clothing/useClothing";
import ProductCard from "../components/ProductCard";

const GALLERY_PAGE_SIZE = 4;

function ProductPage() {
  const [searchParams] = useSearchParams();
  const id = searchParams.get("id");
  const navigate = useNavigate();
  const { isLoggedIn } = useCurrentUser();

  const { clothing: product, isLoading, isError } = useClothingDetail(id);
  const { clothes } = useClothingList();

  const [selectedSize, setSelectedSize] = useState(null);
  const [selectedPhoto, setSelectedPhoto] = useState(0);
  const [galleryPage, setGalleryPage] = useState(0);

  // Доступні розміри для вибору
  const sizes = ["XS", "S", "M", "L", "XL", "XXL"];

  useEffect(() => {
    setSelectedPhoto(0);
    setGalleryPage(0);
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

  if (!id) {
    return (
      <div
        style={{
          padding: "50px",
          textAlign: "center",
          color: "#3D5690",
          fontSize: "18px",
        }}
      >
        Товар не вказано.
      </div>
    );
  }

  if (isError) {
    return (
      <div
        style={{
          padding: "50px",
          textAlign: "center",
          color: "#3D5690",
          fontSize: "18px",
        }}
      >
        Не вдалося завантажити товар.
      </div>
    );
  }

  if (isLoading || !product) {
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

  const photos = product.photos?.filter(Boolean) || [];
  const photoSrc = photos[selectedPhoto] || "/hoodie.png";
  const relatedProducts = clothes.filter((item) => item.id !== product.id);
  const galleryPageCount = Math.ceil(
    relatedProducts.length / GALLERY_PAGE_SIZE,
  );
  const galleryProducts = relatedProducts.slice(
    galleryPage * GALLERY_PAGE_SIZE,
    galleryPage * GALLERY_PAGE_SIZE + GALLERY_PAGE_SIZE,
  );

  return (
    <main className="product-page container">
      <div className="product-main-content">
        <div className="product-visuals">
          <div className="product-image-card">
            <img src={photoSrc} alt={product.name || "Товар"} />
          </div>
          {photos.length > 0 && (
            <div className="thumbnail-list">
              {photos.map((photo, index) => (
                <button
                  className={`thumbnail-card ${
                    selectedPhoto === index ? "active" : ""
                  }`}
                  key={index}
                  onClick={() => setSelectedPhoto(index)}
                  type="button"
                >
                  <img
                    src={photo}
                    alt={`${product.name || "Товар"} ${index + 1}`}
                  />
                </button>
              ))}
            </div>
          )}
        </div>

        <div className="">
          <div className="product-details">
            <div className="info-section">
              <h2 className="product-title">{product.name}</h2>
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
          {galleryProducts.length > 0 && (
            <div className="bottom-gallery">
              <button
                className="gallery-arrow gallery-arrow--previous"
                disabled={galleryPage === 0}
                onClick={() => setGalleryPage((page) => page - 1)}
                type="button"
                aria-label="Попередні товари"
              >
                ‹
              </button>
              <div className="bottom-gallery-track" key={galleryPage}>
                {galleryProducts.map((item) => (
                  <Link
                    className="gallery-card"
                    key={item.id}
                    to={`/product?id=${item.id}`}
                  >
                    <ProductCard product={item} />
                  </Link>
                ))}
              </div>
              <button
                className="gallery-arrow gallery-arrow--next"
                disabled={galleryPage >= galleryPageCount - 1}
                onClick={() => setGalleryPage((page) => page + 1)}
                type="button"
                aria-label="Наступні товари"
              >
                ›
              </button>
            </div>
          )}
        </div>
      </div>
    </main>
  );
}

export default ProductPage;
