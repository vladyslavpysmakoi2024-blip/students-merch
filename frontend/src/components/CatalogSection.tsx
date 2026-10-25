import React from "react";
import ProductGrid from "@components/ProductGrid";
import { shopperTypeLabel } from "@shared/lib/clothingType";
import { ClothingItem } from "@shared/types/api";

interface CatalogSectionProps {
  products?: ClothingItem[];
  isLoading?: boolean;
  isError?: boolean;
}

function CatalogSection({
  products = [],
  isLoading = false,
  isError = false,
}: CatalogSectionProps) {
  const groupedProducts = products.reduce<Record<string, ClothingItem[]>>(
    (acc, val) => {
      const key = shopperTypeLabel(val.type);
      if (!acc[key]) {
        acc[key] = [];
      }
      acc[key].push(val);
      return acc;
    },
    {},
  );

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
