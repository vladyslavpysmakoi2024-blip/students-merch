import ProductCard from "./ProductCard";
import { Link } from "react-router-dom";

function CatalogSection({ products, isLoading, isError }) {
  return (
    <section className="catalog">
      <div className="catalog-title-wrapper">
        <h2 className="catalog-title">КАТАЛОГ</h2>
      </div>

      <div className="product-grid">
        {isLoading ? (
          <div className="product-list-state">Завантаження...</div>
        ) : isError ? (
          <div className="product-list-state">
            Не вдалося завантажити товари.
          </div>
        ) : products.length > 0 ? (
          products.map((product) => (
            <Link
              key={product.id}
              to={`/product?id=${product.id}`}
              style={{ textDecoration: "none", display: "contents" }}
            >
              <ProductCard product={product} />
            </Link>
          ))
        ) : (
          <div className="product-list-state">Наразі товарів немає.</div>
        )}
      </div>
    </section>
  );
}

export default CatalogSection;
