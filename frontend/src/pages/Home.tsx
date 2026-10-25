import Hero from "@components/Hero";
import CatalogSection from "@components/CatalogSection";
import { useClothingList } from "@features/clothing/useClothing";

function Home() {
  const { clothes, isLoading, isError } = useClothingList();

  return (
    <main className="home">
      <div className="container">
        <div className="layout">
          <div className="main-content">
            <Hero />
            <CatalogSection
              products={clothes}
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
