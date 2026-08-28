import React from 'react';
import ProductCard from '../components/ProductCard';
import { Link } from 'react-router-dom';
import '../App.css'; // Make sure styles are imported if not globally available

const mockFavorites = [
  { id: 1, name: 'Круте худі', price: 900 },
  { id: 2, name: 'Світшот', price: 800 },
  { id: 3, name: 'Футболка з принтом', price: 450 },
  { id: 4, name: 'Штани карго', price: 1200 }
];

function FavoritesPage() {
  return (
    <main className="search-page favorites-page" style={{ paddingTop: '50px', paddingBottom: '50px' }}>
      <div className="container" style={{ position: 'relative' }}>

        <div className="favorites-header">
          {/* Збережи картинку котика в папку public під назвою cat-thumbs-up.png */}
          <img src="/cat-thumbs-up.png" alt="cat thumbs up" className="cat-header-mascot" />
          <h2 className="search-title title-pill">Мої вподобання</h2>
        </div>
        
        <div className="favorites-list" style={{ position: 'relative', zIndex: 2 }}>
          {mockFavorites.map(item => (
            <div className="favorite-item-row" key={item.id}>
              <Link to={`/product?id=${item.id}`} className="fav-item-link">
                <div className="fav-image-placeholder">
                  <span className="fav-photo-icon">📷</span>
                </div>
                <div className="fav-details">
                  <h3 className="fav-name">{item.name}</h3>
                  <p className="fav-price">{item.price} ₴</p>
                  <div className="fav-meta">
                    <span className="fav-badge">В наявності</span>
                  </div>
                </div>
              </Link>
              <div className="fav-actions">
                <button className="btn-add-cart">У кошик</button>
                <button className="btn-remove-fav">
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <line x1="18" y1="6" x2="6" y2="18"></line>
                    <line x1="6" y1="6" x2="18" y2="18"></line>
                  </svg>
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </main>
  );
}

export default FavoritesPage;
