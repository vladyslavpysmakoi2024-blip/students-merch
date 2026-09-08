import ProductCard from "./ProductCard";
import { Link } from "react-router-dom";

function CatalogSection() {
  return (
    <section className="catalog">
      <div className="catalog-title-wrapper">
        <h2 className="catalog-title">КАТАЛОГ</h2>
      </div>

      <div className="product-grid">
        {Array.from({ length: 7 }).map((_, i) => (
          <Link key={i} to="/product" style={{ textDecoration: 'none', display: 'contents' }}>
            <ProductCard />
          </Link>
        ))}
      </div>
    </section>
  );
}

export default CatalogSection;