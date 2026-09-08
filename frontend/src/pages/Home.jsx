import Hero from "../components/Hero";
import CatalogSection from "../components/CatalogSection";
import ProductCard from "../components/ProductCard";
import { Link } from "react-router-dom";

function Home() {
  return (
    <main className="home">
      <div className="container">
        <div className="layout">
          <div className="main-content">
            <Hero />
            <CatalogSection />
          </div>
          
          <aside className="right-sidebar">
            <Link to="/product" style={{ textDecoration: 'none', display: 'contents' }}>
              <ProductCard variant="large" />
            </Link>
            <Link to="/product" style={{ textDecoration: 'none', display: 'contents' }}>
              <ProductCard variant="large" />
            </Link>
          </aside>
        </div>
      </div>
    </main>
  );
}

export default Home;