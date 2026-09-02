import React, { useEffect, useState } from "react";
import ProductGrid from "./ProductGrid";
import { Link } from "react-router-dom";
import { api } from "../shared/api/instance";

function CatalogSection() {
  const [products, setProducts] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  const groupedProducts = products.reduce((acc, val) => {
    const key = val.type;
    
    if (!acc[key]) {
      acc[key] = [];
    }
    
    acc[key].push(val);

    return acc;
  }, {});

  useEffect(() => {
    const SetData = async () => {
      try {
        const response = await api.get("/clothing/simple-list");
        const data = response.data;

        setProducts(data);
      }
      catch(ex) {
        console.log(`Error fetching clothing: ${ex}`);
      }
      finally{
        setIsLoading(false);
      }
    }

    
    SetData();
  }, [])

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

  return (
    <section className="catalog">
      <div className="catalog-title-wrapper">
        <h2 className="catalog-title">КАТАЛОГ</h2>
      </div>

      {groupedProducts && Object.entries(groupedProducts).map(([ctg, arr]) => {
        return(
          <ProductGrid key={ctg} ctg={ctg} items={arr} />
        )
      })}

    </section>
  );
}

export default CatalogSection;