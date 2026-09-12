import React, { useRef, useLayoutEffect, useState } from 'react'
import ProductCard from './ProductCard';

const ModelGrid = ({ ctg, items, setActiveModels }) => {

  return (
    <div className='product-container' >
      <div className='product-ctg' >{ctg}</div>
      <div className="product-grid">
        {items.map((i) => {
          return (
            <div key={i.id} style={{ cursor: "pointer" }} onClick={() => {
                setActiveModels((pr) => {
                    return pr.map((m) => m["type"] === i["type"] ? i : pr)
                })
            }} >
                <ProductCard product={i} />
            </div>
          )
        })}
      </div>
    </div>
  )
}

export default ModelGrid