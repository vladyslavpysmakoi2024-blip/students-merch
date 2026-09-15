import React, { useEffect, useState } from "react";
import ProductGrid from "./ProductGrid";
import { api } from "../shared/api/instance";

function CatalogSection() {
  const [products, setProducts] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isError, setIsError] = useState(false);

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

  return (
    <section className="catalog">
      <div className="catalog-title-wrapper">
        <h2 className="catalog-title">КАТАЛОГ</h2>
      </div>

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
