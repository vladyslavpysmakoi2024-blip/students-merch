import React, { useState } from "react";
import { useLocation, Link } from "react-router-dom";
import ProductCard from "../components/ProductCard";
import { useClothingSearch } from "../features/clothing/useClothing";

const TYPES = [
  "Джинси",
  "Майка",
  "Куртка",
  "Светр",
  "Джегінси",
  "Спідниця",
  "Жилетка",
  "Блейзер",
  "Кардиган",
  "Футболка",
  "Сукня",
  "Світшот",
  "Шорти",
  "Сорочка",
  "Худі",
  "Штани",
  "Бомбер",
  "Пальто",
  "Топ",
  "Поло",
];
const COLORS = [
  "Пісочний",
  "Сірий",
  "Темно-сірий",
  "Коричневий",
  "Оливковий",
  "Квітковий",
  "Джинсовий",
  "Червоний",
  "Синій",
  "Білий",
  "Клітинка",
  "Темно-синій",
  "Жовтий",
  "Рожевий",
  "Бордовий",
  "Чорний",
  "Блакитний",
  "Бежевий",
  "Зелений",
  "Гірчичний",
];
const SIZES = ["XS", "S", "M", "L", "XL", "XXL"];

function SearchPage() {
  const location = useLocation();
  const searchParams = new URLSearchParams(location.search);
  const query = searchParams.get("q") || "";

  // Стейт фільтрів
  const [clothingType, setClothingType] = useState("");
  const [color, setColor] = useState("");
  const [size, setSize] = useState("");
  const [minPrice, setMinPrice] = useState("");
  const [maxPrice, setMaxPrice] = useState("");

  // Отримання списку товарів та фільтрація
  const { results, loading, isFiltering } = useClothingSearch({
    query,
    clothingType,
    color,
    size,
    minPrice,
    maxPrice,
  });

  return (
    <main className="search-page">
      <div className="container">
        <div className="layout">
          {/* Лівий сайдбар для фільтрів */}
          <aside className="left-sidebar filter-sidebar">
            <h3 className="filter-title">Фільтри</h3>

            <div className="filter-group">
              <label>Категорія:</label>
              <select
                value={clothingType}
                onChange={(e) => setClothingType(e.target.value)}
              >
                <option value="">Всі категорії</option>
                {TYPES.sort().map((t) => (
                  <option key={t} value={t}>
                    {t}
                  </option>
                ))}
              </select>
            </div>

            <div className="filter-group">
              <label>Колір:</label>
              <select value={color} onChange={(e) => setColor(e.target.value)}>
                <option value="">Всі кольори</option>
                {COLORS.sort().map((c) => (
                  <option key={c} value={c}>
                    {c}
                  </option>
                ))}
              </select>
            </div>

            <div className="filter-group">
              <label>Розмір:</label>
              <select value={size} onChange={(e) => setSize(e.target.value)}>
                <option value="">Всі розміри</option>
                {SIZES.map((s) => (
                  <option key={s} value={s}>
                    {s}
                  </option>
                ))}
              </select>
            </div>

            <div className="filter-group">
              <label>Ціна (₴):</label>
              <div className="price-inputs">
                <input
                  type="number"
                  placeholder="Від"
                  value={minPrice}
                  onChange={(e) => setMinPrice(e.target.value)}
                  min="0"
                />
                <span> - </span>
                <input
                  type="number"
                  placeholder="До"
                  value={maxPrice}
                  onChange={(e) => setMaxPrice(e.target.value)}
                  min="0"
                />
              </div>
            </div>

            <button
              className="clear-filters-btn"
              onClick={() => {
                setClothingType("");
                setColor("");
                setSize("");
                setMinPrice("");
                setMaxPrice("");
              }}
              style={{ display: isFiltering ? "block" : "none" }}
            >
              Скинути фільтри
            </button>
          </aside>

          {/* Основний контент з результатами */}
          <div className="main-content">
            <div className="search-header">
              <h2 className="search-title">
                {isFiltering
                  ? "Результати за фільтрами"
                  : query
                    ? `Результати пошуку для "${query}"`
                    : "Всі товари"}
              </h2>
              <p className="search-count">Знайдено: {results.length} товарів</p>
            </div>

            {loading ? (
              <div
                style={{
                  padding: "30px",
                  textAlign: "center",
                  color: "#3d5690",
                }}
              >
                Завантаження...
              </div>
            ) : (
              <div className="search-results-grid">
                {results.length > 0 ? (
                  results.map((item) => (
                    <Link
                      key={item.id}
                      to={`/product?id=${item.id}`}
                      style={{ textDecoration: "none", display: "contents" }}
                    >
                      <ProductCard product={item} />
                    </Link>
                  ))
                ) : (
                  <div
                    style={{
                      gridColumn: "1 / -1",
                      textAlign: "center",
                      color: "#3d5690",
                    }}
                  >
                    За вашим запитом нічого не знайдено.
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </main>
  );
}

export default SearchPage;
