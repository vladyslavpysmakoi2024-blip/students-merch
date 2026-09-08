function ProductCard({ variant, product }) {
  console.log(product);
  return (
    <div
      className={`product-card ${
        variant === "large" ? "product-card--large" : ""
      }`}
    >
      {/* {product.photo ? <img src={product.photo} alt="" /> : <div></div>} */}
      {/* Тимчасово порожня картка, дизайн якої ви затвердите з командою */}
    </div>
  );
}

export default ProductCard;
