import "../App.css";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  useCurrentUser,
  useLogout,
  useUpdatePassword,
  useUpdateUser,
} from "../features/auth/useAuth";

function ProfilePage() {
  const navigate = useNavigate();
  const { user, isLoading } = useCurrentUser();
  const { mutate: updateUser } = useUpdateUser();
  const { mutate: updatePassword } = useUpdatePassword();
  const { mutate: logout } = useLogout();

  const [editForm, setEditForm] = useState({
    first_name: user?.first_name || "",
    last_name: user?.last_name || "",
    email: user?.email || "",
    phone_number: user?.phone_number || "",
  });
  const [passwordForm, setPasswordForm] = useState({
    currentPassword: "",
    newPassword: "",
    confirmPassword: "",
  });

  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [isPasswordModalOpen, setIsPasswordModalOpen] = useState(false);

  const wishlist = [
    {
      id: 1,
      title: "ХУДІ З ЛОГОТИПОМ",
      details: "Розмір: M · Колір: Синій",
      price: "1800 грн",
    },
    {
      id: 2,
      title: "ФУТБОЛКА ПОЛІТЕХНІКИ",
      details: "Розмір: L · Колір: Білий",
      price: "950 грн",
    },
  ];

  const saved = [
    {
      id: 1,
      title: "СВІТШОТ OVERSIZE",
      details: "Може, потім, колись :[",
      price: "1600 грн",
    },
    {
      id: 2,
      title: "ШОПЕР З ПРИНТОМ",
      details: "Однозначно куплю після стипендії",
      price: "850 грн",
    },
  ];

  const orders = [
    {
      id: 1,
      number: "№ 10248",
      date: "12.03.2026",
      status: "Доставлено",
      total: "1800 грн",
    },
    {
      id: 2,
      number: "№ 10115",
      date: "03.03.2026",
      status: "В обробці",
      total: "950 грн",
    },
  ];

  const cards = [
    {
      id: 1,
      type: "Visa",
      number: "**** 7777",
      expires: "09/27",
      holder: "HORBATIUK DANYLO",
    },
    {
      id: 2,
      type: "Mastercard",
      number: "**** 7777",
      expires: "04/28",
      holder: "HORBATIUK DANYLO",
    },
  ];

  useEffect(() => {
    const isAnyModalOpen = isEditModalOpen || isPasswordModalOpen;
    document.body.style.overflow = isAnyModalOpen ? "hidden" : "auto";

    const handleEsc = (e) => {
      if (e.key === "Escape") {
        setIsEditModalOpen(false);
        setIsPasswordModalOpen(false);
      }
    };

    window.addEventListener("keydown", handleEsc);

    return () => {
      document.body.style.overflow = "auto";
      window.removeEventListener("keydown", handleEsc);
    };
  }, [isEditModalOpen, isPasswordModalOpen]);

  const openEditModal = () => {
    setEditForm({
      first_name: user.first_name,
      last_name: user.last_name,
      email: user.email,
      phone_number: user.phone_number,
    });
    setIsPasswordModalOpen(false);
    setIsEditModalOpen(true);
  };

  const closeEditModal = () => {
    setIsEditModalOpen(false);
  };

  const saveProfile = async () => {
    console.log(editForm);
    if (
      !editForm.first_name.trim() ||
      !editForm.last_name.trim() ||
      !editForm.email.trim() ||
      !editForm.phone_number.trim()
    ) {
      alert("Заповніть обов'язкові поля профілю.");
      return;
    }

    updateUser(
      {
        first_name: editForm.first_name.trim(),
        last_name: editForm.last_name.trim(),
        email: editForm.email.trim(),
        phone_number: editForm.phone_number.trim(),
      },
      {
        onSuccess: () => {
          setIsEditModalOpen(false);
        },
        onError: () => {
          alert("Помилка оновлення");
        },
      },
    );
  };

  const openPasswordModal = () => {
    setPasswordForm({
      currentPassword: "",
      newPassword: "",
      confirmPassword: "",
    });
    setIsEditModalOpen(false);
    setIsPasswordModalOpen(true);
  };

  const closePasswordModal = () => {
    setIsPasswordModalOpen(false);
  };

  const savePassword = () => {
    const { currentPassword, newPassword, confirmPassword } = passwordForm;

    if (!currentPassword || !newPassword || !confirmPassword) {
      alert("Заповни всі поля для зміни пароля.");
      return;
    }

    if (newPassword.length < 6) {
      alert("Новий пароль має містити щонайменше 6 символів.");
      return;
    }

    if (newPassword !== confirmPassword) {
      alert("Новий пароль і підтвердження не збігаються.");
      return;
    }

    updatePassword(
      {
        current_password: currentPassword,
        new_password: newPassword,
      },
      {
        onSuccess: () => {
          setIsPasswordModalOpen(false);
          alert("Пароль змінено.");
        },
        onError: () => {
          alert("Помилка оновлення");
        },
        onSettled: () => {
          setPasswordForm({
            currentPassword: "",
            newPassword: "",
            confirmPassword: "",
          });
        },
      },
    );
  };

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  const handleEditFormChange = (e) => {
    const { name, value } = e.target;
    setEditForm((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handlePasswordFormChange = (e) => {
    const { name, value } = e.target;
    setPasswordForm((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const renderCardLogo = (type) => {
    if (type === "Visa") {
      return (
        <div className="payment-logo payment-logo--visa">
          <span>VISA</span>
        </div>
      );
    }

    if (type === "Mastercard") {
      return (
        <div className="payment-logo payment-logo--mc">
          <span className="mc-circle mc-circle--left"></span>
          <span className="mc-circle mc-circle--right"></span>
        </div>
      );
    }

    return <div className="payment-logo">{type}</div>;
  };

  return (
    <>
      <main className="profile-page container">
        <section className="profile-hero">
          <img src="/cat.2.png" alt="" className="profile-decor-cat" />

          <div className="profile-hero-main">
            <div className="profile-avatar-wrap">
              <img src="/cat.1.png" alt="avatar" className="profile-avatar" />
            </div>

            <div className="profile-hero-content">
              <div className="profile-badge">ОСОБИСТИЙ КАБІНЕТ</div>
              <h1 className="profile-name">{`${user.first_name} ${user.last_name}`}</h1>

              <div className="profile-contact-grid">
                <div className="profile-contact-box">
                  <span className="profile-contact-label">
                    Електронна адреса
                  </span>
                  <span className="profile-contact-value">{user.email}</span>
                </div>

                <div className="profile-contact-box">
                  <span className="profile-contact-label">Номер телефону</span>
                  <span className="profile-contact-value">
                    {user.phone_number}
                  </span>
                </div>
              </div>
            </div>
          </div>

          <div className="profile-hero-actions">
            <button className="profile-action-btn" onClick={openEditModal}>
              РЕДАГУВАТИ ПРОФІЛЬ
            </button>

            <button
              className="profile-secondary-outline-btn"
              onClick={openPasswordModal}
            >
              ЗМІНИТИ ПАРОЛЬ
            </button>

            <button className="profile-logout-btn" onClick={handleLogout}>
              ВИЙТИ
            </button>
          </div>
        </section>

        <section className="profile-grid">
          <div className="profile-section-card">
            <div className="profile-section-title-wrapper">
              <h2 className="profile-section-title">ВІШ ЛИСТ</h2>
            </div>

            <div className="profile-items-list">
              {wishlist.map((item) => (
                <div key={item.id} className="profile-item-card">
                  <div className="profile-item-image"></div>

                  <div className="profile-item-content">
                    <h3 className="profile-item-title">{item.title}</h3>
                    <p className="profile-item-details">{item.details}</p>
                  </div>

                  <div className="profile-item-side">
                    <div className="profile-item-price">{item.price}</div>
                    <button
                      className="profile-small-btn"
                      onClick={() =>
                        alert(`Товар "${item.title}" додано в кошик.`)
                      }
                    >
                      У КОШИК
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="profile-section-card">
            <div className="profile-section-title-wrapper">
              <h2 className="profile-section-title">ЗБЕРЕЖЕНЕ</h2>
            </div>

            <div className="profile-items-list">
              {saved.map((item) => (
                <div key={item.id} className="profile-item-card">
                  <div className="profile-item-image profile-item-image--saved"></div>

                  <div className="profile-item-content">
                    <h3 className="profile-item-title">{item.title}</h3>
                    <p className="profile-item-details">{item.details}</p>
                  </div>

                  <div className="profile-item-side">
                    <div className="profile-item-price">{item.price}</div>
                    <button
                      className="profile-secondary-btn"
                      onClick={() => navigate("/product")}
                    >
                      ПЕРЕГЛЯНУТИ
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="profile-section-card">
            <div className="profile-section-title-wrapper">
              <h2 className="profile-section-title">ІСТОРІЯ ЗАМОВЛЕНЬ</h2>
            </div>

            <div className="profile-orders-list">
              {orders.map((order) => (
                <div key={order.id} className="profile-order-card">
                  <div className="profile-order-main">
                    <div className="profile-order-number">{order.number}</div>
                    <div className="profile-order-date">{order.date}</div>
                  </div>

                  <div className="profile-order-status">{order.status}</div>
                  <div className="profile-order-total">{order.total}</div>
                </div>
              ))}
            </div>
          </div>

          <div className="profile-section-card">
            <div className="profile-section-title-wrapper">
              <h2 className="profile-section-title">КАРТКИ ДЛЯ ОПЛАТИ</h2>
            </div>

            <div className="profile-cards-list">
              {cards.map((card) => (
                <div
                  key={card.id}
                  className={`payment-card ${
                    card.type === "Mastercard"
                      ? "payment-card--mc"
                      : "payment-card--visa"
                  }`}
                >
                  <div className="payment-card-top">
                    <div className="payment-card-chip"></div>
                    {renderCardLogo(card.type)}
                  </div>

                  <div className="payment-card-number">{card.number}</div>

                  <div className="payment-card-bottom">
                    <div className="payment-card-holder">
                      <span className="payment-card-label">CARD HOLDER</span>
                      <span>{card.holder}</span>
                    </div>

                    <div className="payment-card-expire">
                      <span className="payment-card-label">EXPIRES</span>
                      <span>{card.expires}</span>
                    </div>
                  </div>
                </div>
              ))}

              <button
                className="add-payment-card-btn"
                onClick={() =>
                  alert("Функцію додавання картки можна підключити пізніше.")
                }
              >
                + ДОДАТИ КАРТКУ
              </button>
            </div>
          </div>
        </section>
      </main>

      {isEditModalOpen && (
        <div className="profile-modal-overlay" onClick={closeEditModal}>
          <div
            className="profile-modal profile-modal--edit"
            onClick={(e) => e.stopPropagation()}
          >
            <button className="profile-modal-close" onClick={closeEditModal}>
              ×
            </button>

            <div className="profile-modal-header">
              <div className="profile-modal-badge">
                <span className="profile-modal-badge-icon">✨</span>
                Мій профіль
              </div>
              <h2 className="profile-modal-title">Оновити дані 💫</h2>
              <p className="profile-modal-subtitle">
                Трохи магії — і профіль стане ідеальним
              </p>
            </div>

            <div className="profile-modal-form profile-modal-form--two-columns">
              <div className="profile-modal-field">
                <label>👤 Прізвище</label>
                <input
                  type="text"
                  name="last_name"
                  value={editForm.last_name}
                  onChange={handleEditFormChange}
                  placeholder="Прізвище"
                />
              </div>

              {/* Ім'я */}
              <div className="profile-modal-field">
                <label>👤 Ім'я</label>
                <input
                  type="text"
                  name="first_name"
                  value={editForm.first_name}
                  onChange={handleEditFormChange}
                  placeholder="Ім'я"
                />
              </div>
              <div className="profile-modal-field">
                <label>📧 Email</label>
                <input
                  type="email"
                  name="email"
                  value={editForm.email}
                  onChange={handleEditFormChange}
                  placeholder="email@example.com"
                />
              </div>

              <div className="profile-modal-field">
                <label>📱 Телефон</label>
                <input
                  type="text"
                  name="phone_number"
                  value={editForm.phone_number}
                  onChange={handleEditFormChange}
                  placeholder="+380..."
                />
              </div>
            </div>

            <div className="profile-modal-footer">
              <span className="profile-modal-note">🐱 Усе можна змінити</span>

              <div className="profile-modal-actions">
                <button
                  className="profile-secondary-outline-btn"
                  onClick={closeEditModal}
                >
                  ← Скасувати
                </button>
                <button className="profile-action-btn" onClick={saveProfile}>
                  💾 Зберегти
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {isPasswordModalOpen && (
        <div className="profile-modal-overlay" onClick={closePasswordModal}>
          <div
            className="profile-modal profile-modal--password"
            onClick={(e) => e.stopPropagation()}
          >
            <button
              className="profile-modal-close"
              onClick={closePasswordModal}
            >
              ×
            </button>

            <div className="profile-modal-header">
              <div className="profile-modal-badge">
                <span className="profile-modal-badge-icon">🔐</span>
                Безпека
              </div>
              <h2 className="profile-modal-title">Новий пароль 🛡️</h2>
              <p className="profile-modal-subtitle">
                Нехай доступ до акаунта буде тільки твоїм
              </p>
            </div>

            <div className="profile-modal-form">
              <div className="profile-modal-field">
                <label>🔑 Поточний пароль</label>
                <input
                  type="password"
                  name="currentPassword"
                  value={passwordForm.currentPassword}
                  onChange={handlePasswordFormChange}
                  placeholder="Поточний пароль"
                />
              </div>

              <div className="profile-modal-field">
                <label>✨ Новий пароль</label>
                <input
                  type="password"
                  name="newPassword"
                  value={passwordForm.newPassword}
                  onChange={handlePasswordFormChange}
                  placeholder="Новий пароль"
                />
              </div>

              <div className="profile-modal-field">
                <label>✅ Підтвердження</label>
                <input
                  type="password"
                  name="confirmPassword"
                  value={passwordForm.confirmPassword}
                  onChange={handlePasswordFormChange}
                  placeholder="Повторіть пароль"
                />
              </div>
            </div>

            <div className="profile-modal-footer">
              <span className="profile-modal-note">🐾 Мінімум 6 символів.</span>

              <div className="profile-modal-actions">
                <button
                  className="profile-secondary-outline-btn"
                  onClick={closePasswordModal}
                >
                  ← Скасувати
                </button>
                <button className="profile-action-btn" onClick={savePassword}>
                  💾 Зберегти
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
}

export default ProfilePage;
