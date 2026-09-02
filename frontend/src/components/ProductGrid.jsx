import React from 'react'
import ProductCard from './ProductCard';
import { Link } from 'react-router-dom';

const ProductGrid = ({ ctg, items }) => {
  return (
    <div className='product-container' >
      <div className='product-ctg' >{ctg}</div>
      <div className="product-grid">
        {items.map((i) => {
          return (
          <Link key={i.id} to={`/product?id=${i.id}`} style={{ textDecoration: 'none', display: 'contents' }}>
            <ProductCard product={i} />
          </Link>)
        })}
      </div>
    </div>
  )
}

export default ProductGrid