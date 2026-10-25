import React, { useRef, useState } from "react";
import { Link } from "react-router-dom";
import ProductCard from "@components/ProductCard";
import { ClothingItem } from "@shared/types/api";

const DRAG_THRESHOLD = 5;

interface ProductGridProps {
  ctg: string;
  items: ClothingItem[];
}

interface DragState {
  startX: number;
  startScrollLeft: number;
  moved: boolean;
}

const ProductGrid = ({ ctg, items }: ProductGridProps) => {
  const parentRef = useRef<HTMLDivElement | null>(null);
  const dragRef = useRef<DragState | null>(null);
  const [isDragging, setIsDragging] = useState(false);

  const handlePointerDown = (e: React.PointerEvent<HTMLDivElement>) => {
    if (e.pointerType !== "mouse" || e.button !== 0 || !parentRef.current)
      return;

    dragRef.current = {
      startX: e.clientX,
      startScrollLeft: parentRef.current.scrollLeft,
      moved: false,
    };
  };

  const handlePointerMove = (e: React.PointerEvent<HTMLDivElement>) => {
    const drag = dragRef.current;
    if (!drag || (e.buttons & 1) === 0 || !parentRef.current) return;

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

  const handleClickCapture = (e: React.MouseEvent<HTMLDivElement>) => {
    if (dragRef.current?.moved) {
      e.preventDefault();
      e.stopPropagation();
    }
    dragRef.current = null;
  };

  return (
    <div className="product-container">
      <div className="product-ctg">{ctg}</div>
      <div
        className={`product-grid ${isDragging ? "product-grid--dragging" : ""}`}
        ref={parentRef}
        onPointerDown={handlePointerDown}
        onPointerMove={handlePointerMove}
        onPointerUp={handlePointerUp}
        onPointerCancel={handlePointerUp}
        onClickCapture={handleClickCapture}
        onDragStart={(e) => e.preventDefault()}
      >
        {items.map((i) => (
          <Link
            key={i.id}
            to={`/product?id=${i.id}`}
            style={{ textDecoration: "none", display: "contents" }}
          >
            <ProductCard product={i} />
          </Link>
        ))}
      </div>
    </div>
  );
};

export default ProductGrid;
