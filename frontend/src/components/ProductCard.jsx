function ProductCard({ variant, product }) {
  return (
    <div
      className={`product-card ${
        variant === "large" ? "product-card--large" : ""
      }`}
    >
      {product?.photo ? <img src={product.photo} alt="" /> : <div></div>}
    </div>
  );
}

export default ProductCard;
