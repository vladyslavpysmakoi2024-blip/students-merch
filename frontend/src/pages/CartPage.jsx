import React from 'react';
import {
  useCart,
  useUpdateCartItemQuantity,
  useRemoveCartItem,
} from '../features/cart/useCart';

function CartPage() {
  const { cart, isLoading, isError } = useCart();
  const updateQuantity = useUpdateCartItemQuantity();
  const removeItem = useRemoveCartItem();

  const handleUpdateQuantity = (cartId, currentQuantity, delta) => {
    const newQuantity = Math.max(1, currentQuantity + delta);
    if (newQuantity === currentQuantity) return;
    updateQuantity.mutate({ cartId, quantity: newQuantity });
  };

  const handleRemoveItem = (cartId) => {
    removeItem.mutate(cartId);
  };

  const total = cart.reduce((sum, item) => sum + item.price * item.quantity, 0);
  const itemsCount = cart.reduce((sum, item) => sum + item.quantity, 0);

  if (isLoading) {
    return (
      <main className="cart-page" style={{ paddingTop: '50px', paddingBottom: '50px' }}>
        <div className="container">
          <div className="favorites-header">
            <img src="/cat-cart.png" alt="cat mascot" className="cat-cart-mascot" />
            <h2 className="search-title title-pill">Моя корзина</h2>
          </div>
          <p>Завантаження кошика...</p>
        </div>
      </main>
    );
  }

  if (isError) {
    return (
      <main className="cart-page" style={{ paddingTop: '50px', paddingBottom: '50px' }}>
        <div className="container">
          <div className="favorites-header">
            <img src="/cat-cart.png" alt="cat mascot" className="cat-cart-mascot" />
            <h2 className="search-title title-pill">Моя корзина</h2>
          </div>
          <p>Не вдалося завантажити кошик. Спробуй оновити сторінку.</p>
        </div>
      </main>
    );
  }

  return (
    <main className="cart-page" style={{ paddingTop: '50px', paddingBottom: '50px' }}>
      <div className="container">
        <div className="favorites-header">
          {/* Маскот для Корзини */}
          <img src="/cat-cart.png" alt="cat mascot" className="cat-cart-mascot" />
          <h2 className="search-title title-pill">Моя корзина</h2>
        </div>

        <div className="cart-layout">
          <div className="cart-items">
            {cart.map(item => (
              <div key={item.cart_id} className="cart-item-row">
                <div className="cart-item-image">
                  {item.photo ? (
                    <img src={item.photo} alt={item.name} />
                  ) : (
                    <span style={{ fontSize: '24px', color: 'rgba(61,86,144,0.3)' }}>📷</span>
                  )}
                </div>
                <div className="cart-item-details">
                  <h3>{item.name}</h3>
                  <div className="cart-item-meta">
                    <span>Колір: {item.color}</span>
                    <span className="dot-separator">•</span>
                    <span>Розмір: {item.size}</span>
                  </div>
                  <p className="cart-item-price-mobile">{item.price} ₴</p>
                </div>
                <div className="cart-item-actions">
                  <div className="quantity-control">
                    <button onClick={() => handleUpdateQuantity(item.cart_id, item.quantity, -1)}>-</button>
                    <span>{item.quantity}</span>
                    <button onClick={() => handleUpdateQuantity(item.cart_id, item.quantity, 1)}>+</button>
                  </div>
                  <div className="cart-item-price">
                    {item.price * item.quantity} ₴
                  </div>
                  <button className="btn-remove-item" onClick={() => handleRemoveItem(item.cart_id)} title="Видалити">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M3 6h18"></path>
                      <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                    </svg>
                  </button>
                </div>
              </div>
            ))}
            {cart.length === 0 && (
              <div className="empty-cart-message">
                <h3>Корзина порожня 😢</h3>
                <p>Час знайти щось круте в каталозі!</p>
              </div>
            )}
          </div>

          <div className="cart-summary-box">
            <h3>Замовлення</h3>
            <div className="summary-details">
              <div className="summary-row">
                <span>Товари ({itemsCount} шт.)</span>
                <span>{total} ₴</span>
              </div>
              <div className="summary-row">
                <span>Доставка</span>
                <span className="shipping-cost">За тарифами пошти</span>
              </div>
            </div>
            <div className="summary-total-row">
              <span>Разом</span>
              <span className="total-price">{total} ₴</span>
            </div>
            <button className="btn-checkout-primary" disabled={cart.length === 0}>
              Оформити замовлення
            </button>
            {/* Збережи потрібного котика під назвою cat-checkout.png у папці public */}
            <img src="/cat-checkout.png" alt="checkout cat" className="cat-checkout-mascot" />
          </div>
        </div>
      </div>
    </main>
  );
}

export default CartPage;
