import Hero from "../components/Hero";
import CatalogSection from "../components/CatalogSection";
import ProductCard from "../components/ProductCard";
import { Link } from "react-router-dom";
import { useClothingList } from "../features/clothing/useClothing";

const CATALOG_COUNT = 7;
const SIDEBAR_COUNT = 2;

function Home() {
  const { clothes, isLoading, isError } = useClothingList();

  const catalogProducts = clothes.slice(0, CATALOG_COUNT);
  const sidebarProducts = clothes.slice(
    CATALOG_COUNT,
    CATALOG_COUNT + SIDEBAR_COUNT,
  );

  return (
    <main className="home">
      <div className="container">
        <div className="layout">
          <div className="main-content">
            <Hero />
            <CatalogSection
              products={catalogProducts}
              isLoading={isLoading}
              isError={isError}
            />
          </div>

          <aside className="right-sidebar">
            {sidebarProducts.map((product) => (
              <Link
                key={product.id}
                to={`/product?id=${product.id}`}
                style={{ textDecoration: "none", display: "contents" }}
              >
                <ProductCard variant="large" product={product} />
              </Link>
            ))}
          </aside>
        </div>
      </div>
    </main>
  );
}

export default Home;
