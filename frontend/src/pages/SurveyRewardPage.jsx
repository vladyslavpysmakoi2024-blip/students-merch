import { useEffect, useState } from "react";
import { Navigate, useLocation, useNavigate } from "react-router-dom";
import SurveyConfetti from "../components/SurveyConfetti";
import { useCurrentUser } from "../features/auth/useAuth";
import {
  findPackageById,
  getSavedPackageId,
  savePackageId,
  SURVEY_DISCOUNT_PERCENT,
  SURVEY_PACKAGES,
} from "../features/survey/packages";

function SurveyRewardPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const { user } = useCurrentUser();
  const justCompleted = Boolean(location.state?.justCompleted);
  const [celebrate, setCelebrate] = useState(Boolean(location.state?.celebrate));
  const [selectedId, setSelectedId] = useState(() => getSavedPackageId(user?.id));
  const [savedId, setSavedId] = useState(() => getSavedPackageId(user?.id));

  useEffect(() => {
    if (!location.state?.celebrate) return;
    const timeoutId = window.setTimeout(() => setCelebrate(false), 3400);
    navigate(".", { replace: true, state: { justCompleted: true } });
    return () => window.clearTimeout(timeoutId);
  }, [location.state, navigate]);

  if (!user?.completed_survey && !justCompleted) {
    return <Navigate to="/survey" replace />;
  }

  const savedPackage = findPackageById(savedId);

  const handleConfirm = () => {
    if (!selectedId) {
      alert("Обери один сет із футболки та шопера.");
      return;
    }
    savePackageId(user.id, selectedId);
    setSavedId(selectedId);
  };

  return (
    <main className="survey-page container">
      <SurveyConfetti active={celebrate} />

      <section className="survey-hero">
        <div className="survey-hero-copy">
          <div className="survey-badge">БОНУС ЗА ВАЙБ</div>
          <h1 className="survey-title">Обери свій сет</h1>
          <p className="survey-subtitle">
            2 футболки × 3 шопери = 6 сетів. Один із них — зі знижкою{" "}
            {SURVEY_DISCOUNT_PERCENT}%.
          </p>
        </div>
      </section>

      {savedPackage && (
        <p className="survey-package-saved">
          Зараз обрано: {savedPackage.tshirt.name} + {savedPackage.tote.name}
        </p>
      )}

      <section className="survey-packages">
        {SURVEY_PACKAGES.map((pack) => {
          const selected = selectedId === pack.id;
          return (
            <button
              key={pack.id}
              type="button"
              className={`survey-package-card${selected ? " is-selected" : ""}`}
              onClick={() => setSelectedId(pack.id)}
              aria-pressed={selected}
            >
              <span className="survey-package-discount">
                −{pack.discountPercent}%
              </span>
              <div className="survey-package-mocks">
                <div className={`survey-mock survey-mock-tee survey-mock--${pack.tshirt.id}`}>
                  <span>Tee</span>
                </div>
                <div className={`survey-mock survey-mock-tote survey-mock--${pack.tote.id}`}>
                  <span>Tote</span>
                </div>
              </div>
              <h2 className="survey-package-title">
                {pack.tshirt.name} + {pack.tote.name}
              </h2>
              <p className="survey-package-meta">
                {pack.tshirt.color} · {pack.tote.color}
              </p>
              <p className="survey-package-price">
                <span className="survey-package-price-old">{pack.price} грн</span>
                <span>{pack.discountedPrice} грн</span>
              </p>
            </button>
          );
        })}
      </section>

      <div className="survey-actions">
        <button
          type="button"
          className="profile-secondary-outline-btn"
          onClick={() => navigate("/me")}
        >
          ПІЗНІШЕ
        </button>
        <button
          type="button"
          className="profile-action-btn survey-submit"
          onClick={handleConfirm}
          disabled={!selectedId}
        >
          {savedId && savedId === selectedId
            ? "СЕТ ЗБЕРЕЖЕНО"
            : `ЗАБРАТИ −${SURVEY_DISCOUNT_PERCENT}%`}
        </button>
      </div>
    </main>
  );
}

export default SurveyRewardPage;
