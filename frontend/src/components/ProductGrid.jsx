import React, { useRef, useLayoutEffect, useState } from 'react'
import ProductCard from './ProductCard';
import { Link } from 'react-router-dom';

const ProductGrid = ({ ctg, items }) => {
  const parentRef = useRef(null);
  const [hasHidden, setHasHidden] = useState(false);

  useLayoutEffect(() => {
    const container = parentRef.current;

    const checkOverflow = () => {
      const parentRect = container.getBoundingClientRect();
      const children = Array.from(container.children);

      const anyHidden = children.some((child) => {
        const targetEl = child.firstElementChild || child;
        const childRect = targetEl.getBoundingClientRect();

        return childRect.bottom > parentRect.bottom + 1;
      })

      setHasHidden(anyHidden);
    }

    checkOverflow();

    const observer = new ResizeObserver(checkOverflow);
    observer.observe(container);

    return () => observer.disconnect();

  }, [items])


  return (
    <div className='product-container' >
      <div className='product-ctg' >{ctg}</div>
      <div className="product-grid" ref={parentRef} >
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