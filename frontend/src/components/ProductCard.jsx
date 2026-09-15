function ProductCard({ variant, product }) {
  const photoSrc = product?.photos?.[0];

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
          alt={product.name || "Товар"}
        />
      )}

      <div className="product-card-content">
        <h3 className="product-card-title">{product.name || "Без назви"}</h3>

        {(product.type || product.color) && (
          <p className="product-card-meta">
            {[product.type, product.color].filter(Boolean).join(" · ")}
          </p>
        )}

        <p className="product-card-price">
          {product.price != null ? `${product.price} ₴` : "Ціна уточнюється"}
        </p>
      </div>
    </div>
  );
}

export default ProductCard;
