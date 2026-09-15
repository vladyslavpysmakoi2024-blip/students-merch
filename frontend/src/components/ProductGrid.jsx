import React, { useRef, useState } from 'react'
import ProductCard from './ProductCard';
import { Link } from 'react-router-dom';

const DRAG_THRESHOLD = 5;

const ProductGrid = ({ ctg, items }) => {
  const parentRef = useRef(null);
  const dragRef = useRef(null);
  const [isDragging, setIsDragging] = useState(false);

  const handlePointerDown = (e) => {
    if (e.pointerType !== 'mouse' || e.button !== 0) return;

    dragRef.current = {
      startX: e.clientX,
      startScrollLeft: parentRef.current.scrollLeft,
      moved: false,
    };
  };

  const handlePointerMove = (e) => {
    const drag = dragRef.current;
    if (!drag || (e.buttons & 1) === 0) return;

    const deltaX = e.clientX - drag.startX;

    if (!drag.moved) {
      if (Math.abs(deltaX) < DRAG_THRESHOLD) return;

      drag.moved = true;
      parentRef.current.setPointerCapture(e.pointerId);
      setIsDragging(true);
    }

    parentRef.current.scrollLeft = drag.startScrollLeft - deltaX;
  };

  const handlePointerUp = () => {
    if (!dragRef.current?.moved) {
      dragRef.current = null;
    }
    setIsDragging(false);
  };

  const handleClickCapture = (e) => {
    if (dragRef.current?.moved) {
      e.preventDefault();
      e.stopPropagation();
    }
    dragRef.current = null;
  };

  return (
    <div className='product-container' >
      <div className='product-ctg' >{ctg}</div>
      <div
        className={`product-grid ${isDragging ? 'product-grid--dragging' : ''}`}
        ref={parentRef}
        onPointerDown={handlePointerDown}
        onPointerMove={handlePointerMove}
        onPointerUp={handlePointerUp}
        onPointerCancel={handlePointerUp}
        onClickCapture={handleClickCapture}
        onDragStart={(e) => e.preventDefault()}
      >
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