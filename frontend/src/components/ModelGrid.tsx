import React from "react";
import ProductCard from "@components/ProductCard";
import { ClothingItem } from "@shared/types/api";

interface ModelGridProps {
  ctg: string;
  items: ClothingItem[];
  setActiveModels: React.Dispatch<React.SetStateAction<ClothingItem[]>>;
  activeModels: ClothingItem[];
}

const ModelGrid = ({
  ctg,
  items,
  setActiveModels,
  activeModels,
}: ModelGridProps) => {
  return (
    <div className="product-container">
      <div className="product-ctg">{ctg}</div>
      <div className="product-grid model-grid">
        {items.map((i) => {
          const isActive = activeModels.some((m) => m.id === i.id);
          return (
            <div
              key={i.id}
              style={{
                cursor: "pointer",
                ...(isActive
                  ? { border: "2px solid #3d5690", borderRadius: "20px" }
                  : {}),
              }}
              onClick={() => {
                setActiveModels((pr) => {
                  const exists = pr.some((m) => m.type === i.type);

                  if (exists) {
                    return pr.map((m) => (m.type === i.type ? i : m));
                  }

                  return [...pr, i];
                });
              }}
            >
              <ProductCard product={i} />
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default ModelGrid;
