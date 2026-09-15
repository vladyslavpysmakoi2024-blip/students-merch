import React, { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";

const MOCK_ORDER = {
  id: 12345,
  name: "Military Windbreaker",
  price: 2200,
  color: "Синій",
  size: "M",
  qty: 1,
  image: "https://via.placeholder.com/80x80?text=Jacket",
};

function CheckoutPage() {
  const navigate = useNavigate();
  const [step, setStep] = useState(1);
  const [paymentMethod, setPaymentMethod] = useState("card");

  // Обробка фейкової оплати
  useEffect(() => {
    if (step === 4) {
      const timer = setTimeout(() => {
        // Для тестування помилки можна змінити на setStep(6)
        setStep(5);
      }, 2500);
      return () => clearTimeout(timer);
    }
  }, [step]);

  const handleNext = () => setStep((prev) => prev + 1);
  const handleBack = () => setStep((prev) => prev - 1);
  const handleTryAgain = () => setStep(2);

  return (
    <main className="checkout-page">
      <div className="checkout-container">
        <div className="checkout-card">
          {/* Stepper (Кроки) - показуємо тільки на 1-3 кроках */}
          {step <= 3 && (
            <div className="stepper">
              <div className={`step ${step >= 1 ? "active" : ""}`}>
                <div className="step-circle">1</div>
                <div className="step-label">Оплата</div>
              </div>
              <div className={`step-line ${step >= 2 ? "active" : ""}`}></div>
              <div className={`step ${step >= 2 ? "active" : ""}`}>
                <div className="step-circle">2</div>
                <div className="step-label">Підтвердження</div>
              </div>
            </div>
          )}

          {/* КРОК 1: Підтвердження замовлення */}
          {step === 1 && (
            <div className="checkout-step-content">
              <h2 className="checkout-title">Ваше замовлення</h2>
              <div className="order-summary-item">
                <img
                  src={MOCK_ORDER.image}
                  alt="product"
                  className="order-image"
                />
                <div className="order-details">
                  <h3>{MOCK_ORDER.name}</h3>
                  <p>
                    Колір: {MOCK_ORDER.color} • Розмір: {MOCK_ORDER.size}
                  </p>
                </div>
                <div className="order-price-wrap">
                  <div className="order-price">{MOCK_ORDER.price} ₴</div>
                  <div className="order-qty">{MOCK_ORDER.qty} шт.</div>
                </div>
              </div>

              <div className="order-total-row">
                <span>Разом</span>
                <span className="total-price">{MOCK_ORDER.price} ₴</span>
              </div>

              <div className="user-info-box">
                <div className="user-avatar-placeholder">👤</div>
                <div>
                  <div className="user-info-title">Дані отримувача</div>
                  <div className="user-info-subtitle">
                    Підтягуються з вашого профілю
                  </div>
                </div>
              </div>

              <div className="checkout-actions right">
                <button className="btn-checkout-primary" onClick={handleNext}>
                  Перейти до оплати →
                </button>
              </div>
            </div>
          )}

          {/* КРОК 2: Вибір способу оплати */}
          {step === 2 && (
            <div className="checkout-step-content">
              <h2 className="checkout-title">Спосіб оплати</h2>
              <div className="payment-methods">
                <label
                  className={`payment-method-box ${paymentMethod === "card" ? "selected" : ""}`}
                >
                  <input
                    type="radio"
                    name="payment"
                    value="card"
                    checked={paymentMethod === "card"}
                    onChange={() => setPaymentMethod("card")}
                  />
                  <div className="method-info">
                    <span className="method-icon">💳</span>
                    <div>
                      <div className="method-name">Банківська картка</div>
                      <div className="method-desc">Visa, Mastercard</div>
                    </div>
                  </div>
                  <div className="method-logos">
                    <span style={{ color: "#1434CB", fontWeight: "bold" }}>
                      VISA
                    </span>
                    <span style={{ color: "#EB001B", marginLeft: "10px" }}>
                      ●●
                    </span>
                  </div>
                </label>

                <label
                  className={`payment-method-box ${paymentMethod === "mono" ? "selected" : ""}`}
                >
                  <input
                    type="radio"
                    name="payment"
                    value="mono"
                    checked={paymentMethod === "mono"}
                    onChange={() => setPaymentMethod("mono")}
                  />
                  <div className="method-info">
                    <span className="method-icon mono-icon">🐈‍⬛</span>
                    <div>
                      <div className="method-name">Monobank</div>
                      <div className="method-desc">Оплата через додаток</div>
                    </div>
                  </div>
                </label>

                <label
                  className={`payment-method-box ${paymentMethod === "gpay" ? "selected" : ""}`}
                >
                  <input
                    type="radio"
                    name="payment"
                    value="gpay"
                    checked={paymentMethod === "gpay"}
                    onChange={() => setPaymentMethod("gpay")}
                  />
                  <div className="method-info">
                    <span className="method-icon">G</span>
                    <div>
                      <div className="method-name">Google Pay</div>
                      <div className="method-desc">Швидка оплата</div>
                    </div>
                  </div>
                </label>
              </div>

              <div className="checkout-actions split">
                <button className="btn-back" onClick={handleBack}>
                  ← Назад
                </button>
                <button className="btn-checkout-primary" onClick={handleNext}>
                  Продовжити →
                </button>
              </div>
            </div>
          )}

          {/* КРОК 3: Введення даних картки */}
          {step === 3 && (
            <div className="checkout-step-content">
              <div className="checkout-title-row">
                <h2 className="checkout-title">Оплата карткою</h2>
                <span className="secure-badge">🔒 Ваші дані захищені</span>
              </div>

              <div className="card-form">
                <div className="input-group">
                  <label>Номер картки</label>
                  <div className="card-input-wrapper">
                    <input type="text" placeholder="1234 5678 9012 3456" />
                    <div className="card-logos-inline">
                      <span style={{ color: "#1434CB", fontWeight: "bold" }}>
                        VISA
                      </span>
                      <span style={{ color: "#EB001B", marginLeft: "10px" }}>
                        ●●
                      </span>
                    </div>
                  </div>
                </div>

                <div className="card-form-row">
                  <div className="input-group">
                    <label>Термін дії</label>
                    <input type="text" placeholder="MM / YY" />
                  </div>
                  <div className="input-group">
                    <label>CVV</label>
                    <input type="text" placeholder="123" />
                  </div>
                </div>

                <div className="input-group">
                  <label>Ім'я на картці</label>
                  <input type="text" placeholder="Як на картці" />
                </div>
              </div>

              <div className="checkout-actions split">
                <button className="btn-back" onClick={handleBack}>
                  ← Назад
                </button>
                <button className="btn-checkout-primary" onClick={handleNext}>
                  Оплатити {MOCK_ORDER.price} ₴
                </button>
              </div>
            </div>
          )}

          {/* КРОК 4: Обробка платежу */}
          {step === 4 && (
            <div className="checkout-status-content">
              <div className="spinner"></div>
              <h2>Оплата в обробці</h2>
              <p>
                Будь ласка, зачекайте. Ми перевіряємо
                <br />
                дані та підтверджуємо платіж.
              </p>
            </div>
          )}

          {/* КРОК 5: Успішна оплата */}
          {step === 5 && (
            <div className="checkout-status-content">
              <div className="success-icon">✓</div>
              <h2>Платіж успішно здійснено!</h2>
              <p>Ваше замовлення №{MOCK_ORDER.id} прийнято в обробку.</p>

              <div className="checkout-actions center column">
                <button
                  className="btn-checkout-primary"
                  onClick={() => navigate("/me")}
                >
                  Перейти до профілю
                </button>
                <button className="btn-text">Деталі замовлення ˅</button>
              </div>
            </div>
          )}

          {/* КРОК 6: Помилка оплати */}
          {step === 6 && (
            <div className="checkout-status-content">
              <div className="error-icon">!</div>
              <h2>Не вдалося провести оплату</h2>
              <p>
                На жаль, сталася помилка під час обробки платежу.
                <br />
                Спробуйте ще раз або оберіть інший спосіб оплати.
              </p>

              <div className="checkout-actions center column">
                <button
                  className="btn-checkout-primary"
                  onClick={handleTryAgain}
                >
                  Спробувати ще раз
                </button>
                <button className="btn-text" onClick={() => setStep(1)}>
                  ← Повернутися до замовлення
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </main>
  );
}

export default CheckoutPage;
