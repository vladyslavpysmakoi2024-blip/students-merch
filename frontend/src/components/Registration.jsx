import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import "../App.css";
import { useLogin, useRegister } from "../features/auth/useAuth";
import { API_BASE_URL } from "../shared/api/instance";

const Registration = () => {
  const [showPassword, setShowPassword] = useState(false);
  const { mutate: register, isPending } = useRegister();
  const { mutate: login, isPending: isLoginPending } = useLogin();
  const navigate = useNavigate();

  const [agreed, setAgreed] = useState(false);
  const [error, setError] = useState("");
  const [form, setForm] = useState({
    firstName: "",
    lastName: "",
    email: "",
    phone: "",
    password: "",
  });

  const handleChange = (e) =>
    setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = (e) => {
    e.preventDefault();
    if (isPending || isLoginPending) return;
    if (
      !form.firstName.trim() ||
      !form.lastName.trim() ||
      !form.email.trim() ||
      !form.phone.trim() ||
      !form.password.trim()
    ) {
      setError("Будь ласка, заповніть всі поля!");
      return;
    }

    if (!agreed) {
      setError("Будь ласка, погодьтесь з умовами використання!");
      return;
    }

    setError("");
    register(
      {
        first_name: form.firstName,
        last_name: form.lastName,
        phone_number: form.phone,
        email: form.email,
        password: form.password,
      },
      {
        onSuccess: () => {
          login(
            { email: form.email, password: form.password },
            {
              onSuccess: () => navigate("/me"),
              onError: () => navigate("/login"),
            },
          );
        },
        onError: (err) => {
          setError(
            err.response?.data?.detail || "Не вдалося зареєструватися",
          );
        },
      },
    );
  };

  return (
    <div className="login-container">
      <div className="registration-wrapper">
        <img src="/cat.3.png" alt="" className="reg-cat reg-cat-left" />
        <img src="/cat.4.png" alt="" className="reg-cat reg-cat-right" />

        <div className="registration-card">
          <div className="registration-header">РЕЄСТРАЦІЯ</div>

          <form className="login-form" onSubmit={handleSubmit}>
            <div className="input-row">
              <div className="input-group">
                <label htmlFor="firstName">Ім'я</label>
                <input
                  id="firstName"
                  name="firstName"
                  type="text"
                  value={form.firstName}
                  onChange={handleChange}
                />
              </div>
              <div className="input-group">
                <label htmlFor="lastName">Прізвище</label>
                <input
                  id="lastName"
                  name="lastName"
                  type="text"
                  value={form.lastName}
                  onChange={handleChange}
                />
              </div>
            </div>

            <div className="input-group">
              <label htmlFor="email">Електронна адреса</label>
              <input
                id="email"
                name="email"
                type="email"
                value={form.email}
                onChange={handleChange}
              />
            </div>

            <div className="input-group">
              <label htmlFor="phone">Номер телефону</label>
              <input
                id="phone"
                name="phone"
                type="tel"
                value={form.phone}
                onChange={handleChange}
              />
            </div>

            <div className="input-group">
              <label htmlFor="password">Пароль</label>
              <div className="password-input-wrapper">
                <input
                  id="password"
                  name="password"
                  type={showPassword ? "text" : "password"}
                  value={form.password}
                  onChange={handleChange}
                  style={{ paddingRight: "60px" }}
                />
                <span
                  className="eye-icon"
                  onClick={() => setShowPassword(!showPassword)}
                  style={{ cursor: "pointer" }}
                  role="button"
                >
                  {showPassword ? (
                    <svg
                      width="24"
                      height="24"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="#3D5690"
                      strokeWidth="2"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    >
                      <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
                      <circle cx="12" cy="12" r="3" />
                    </svg>
                  ) : (
                    <svg
                      width="24"
                      height="24"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="#3D5690"
                      strokeWidth="2"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    >
                      <path d="M1 12s4.2 6 11 6 11-6 11-6" />
                      <path d="M4 14.5l-2 2" />
                      <path d="M20 14.5l2 2" />
                      <path d="M8 17.5l-1 2" />
                      <path d="M12 18.5v2" />
                      <path d="M16 17.5l1 2" />
                    </svg>
                  )}
                </span>
              </div>
            </div>

            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={agreed}
                onChange={(e) => setAgreed(e.target.checked)}
              />
              <span>
                Я погоджуюсь із{" "}
                <a href="#" className="policy-link">
                  Умовами використання
                </a>{" "}
                та{" "}
                <a href="#" className="policy-link">
                  Політикою конфіденційності
                </a>
              </span>
            </label>

            {error && (
              <p style={{ color: "red", fontSize: "13px", margin: "0" }}>
                {error}
              </p>
            )}

            <button type="submit" className="btn-login" disabled={isPending || isLoginPending}>
              Зареєструватися
            </button>

            <div className="divider">
              <span>АБО</span>
            </div>

            <button
              type="button"
              className="btn-google"
              onClick={() =>
                (window.location.href = `${API_BASE_URL}/auth/login/google`)
              }
            >
              <svg width="20" height="20" viewBox="0 0 48 48">
                <path
                  fill="#EA4335"
                  d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z"
                />
                <path
                  fill="#4285F4"
                  d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z"
                />
                <path
                  fill="#FBBC05"
                  d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z"
                />
                <path
                  fill="#34A853"
                  d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.18 1.48-4.97 2.35-8.16 2.35-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z"
                />
              </svg>
              Продовжити з Google
            </button>

            <p className="signup-link">
              Вже маєте обліковий запис? <Link to="/login">Увійти!</Link>
            </p>
          </form>
        </div>
      </div>
    </div>
  );
};

export default Registration;
