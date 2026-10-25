import { shopperTypeLabel } from "@shared/lib/clothingType";
import { clothingPhotoSrc } from "@shared/lib/clothingPhoto";
import { ClothingItem } from "@shared/types/api";

interface ProductCardProps {
  variant?: "large" | "default";
  product?: ClothingItem;
}

function ProductCard({ variant, product }: ProductCardProps) {
  const photoSrc = clothingPhotoSrc(product, 360);

  return (
    <div
      className={`product-card ${
        variant === "large" ? "product-card--large" : ""
      }`}
    >
      {photoSrc && (
        <img
          className="product-card-image"
          src={photoSrc}
          alt={product?.name || "Товар"}
          loading="lazy"
          decoding="async"
        />
      )}

      <div className="product-card-content">
        <h3 className="product-card-title">{product?.name || "Без назви"}</h3>

        {(product?.type || product?.color_name) && (
          <p className="product-card-meta">
            {[shopperTypeLabel(product?.type), product?.color_name]
              .filter(Boolean)
              .join(" · ")}
          </p>
        )}

        <p className="product-card-price">
          {product?.price != null ? `${product.price} ₴` : "Ціна уточнюється"}
        </p>
      </div>
    </div>
  );
}

export default ProductCard;
