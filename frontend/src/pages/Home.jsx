import Hero from "../components/Hero";
import CatalogSection from "../components/CatalogSection";
import { useClothingList } from "../features/clothing/useClothing";

const CATALOG_COUNT = 7;

function Home() {
  const { clothes, isLoading, isError } = useClothingList();

  const catalogProducts = clothes.slice(0, CATALOG_COUNT);

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
        </div>
      </div>
    </main>
  );
}

export default Home;
