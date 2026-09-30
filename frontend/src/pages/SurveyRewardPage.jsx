import { useEffect, useState } from "react";
import { Navigate, useLocation, useNavigate } from "react-router-dom";
import SurveyConfetti from "../components/SurveyConfetti";
import { useCurrentUser } from "../features/auth/useAuth";
import { useAddPackageToCart } from "../features/cart/useCart";
import {
  useClaimPackage,
  useMySurvey,
  useSurveyPackages,
} from "../features/survey/useSurvey";
import {
  findPackageById,
  SURVEY_DISCOUNT_PERCENT,
  SURVEY_PACKAGES,
} from "../features/survey/packages";
import { clothingPhotoSrc } from "../shared/lib/clothingPhoto";

function SurveyRewardPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const { user } = useCurrentUser();
  const { survey, isLoading: surveyLoading } = useMySurvey();
  const { packages: dynamicPackages, isLoading: packagesLoading } =
    useSurveyPackages();
  const { mutate: claimPackage, isPending: isClaiming } = useClaimPackage();
  const { mutate: addPackageToCart, isPending: isAddingToCart } =
    useAddPackageToCart();

  const [cartSuccess, setCartSuccess] = useState(false);
  const justCompleted = Boolean(location.state?.justCompleted);
  const [celebrate, setCelebrate] = useState(Boolean(location.state?.celebrate));

  const assignedPackageId = survey?.assigned_package_id;
  const isConfirmed = Boolean(survey?.is_package_confirmed);
  const [selectedId, setSelectedId] = useState(assignedPackageId || null);

  const packagesList =
    dynamicPackages && dynamicPackages.length > 0
      ? dynamicPackages
      : SURVEY_PACKAGES;

  useEffect(() => {
    if (assignedPackageId) {
      setSelectedId(assignedPackageId);
    }
  }, [assignedPackageId]);

  useEffect(() => {
    if (!location.state?.celebrate) return;
    const timeoutId = window.setTimeout(() => setCelebrate(false), 3400);
    navigate(".", { replace: true, state: { justCompleted: true } });
    return () => window.clearTimeout(timeoutId);
  }, [location.state, navigate]);

  if (
    !user?.completed_survey &&
    !justCompleted &&
    !surveyLoading &&
    !survey
  ) {
    return <Navigate to="/survey" replace />;
  }

  const assignedPackage =
    survey?.package ||
    packagesList.find((p) => p.id === assignedPackageId) ||
    findPackageById(assignedPackageId);

  const currentlyActivePackage =
    packagesList.find((p) => p.id === (selectedId || assignedPackageId)) ||
    assignedPackage ||
    packagesList[0];

  const handleAddToCart = (pkg) => {
    const target = pkg || currentlyActivePackage || assignedPackage;
    if (!target) return;
    if (!isConfirmed) {
      claimPackage(target.id);
    }
    addPackageToCart(
      {
        packageId: target.id,
        tshirtId: target.tshirt.id,
        toteId: target.tote.id,
      },
      {
        onSuccess: () => {
          setCartSuccess(true);
          setTimeout(() => setCartSuccess(false), 3500);
        },
        onError: () => {
          alert("Не вдалося додати сет у кошик. Спробуйте ще раз.");
        },
      },
    );
  };

  return (
    <main className="survey-page container">
      <SurveyConfetti active={celebrate} />

      <section className="survey-hero">
        <div className="survey-hero-copy">
          <div className="survey-badge">БОНУС ЗА ВАЙБ</div>
          <h1 className="survey-title">
            {isConfirmed ? "Твій закріплений сет" : "Обери свій сет зі знижкою"}
          </h1>
          <p className="survey-subtitle">
            {isConfirmed
              ? `Цей сет уже закріплено за твоїм акаунтом зі знижкою ${SURVEY_DISCOUNT_PERCENT}%. Зміна недоступна.`
              : `Обери один із 6 сетів зі знижкою ${SURVEY_DISCOUNT_PERCENT}% та закріпи його за своїм профілем!`}
          </p>
        </div>
      </section>

      {currentlyActivePackage && (
        <div className="survey-package-highlight">
          <span className="survey-package-highlight-tag">
            {isConfirmed
              ? "🔒 ЗАКРІПЛЕНИЙ СЕТ"
              : selectedId === assignedPackageId
              ? "🎲 ТВІЙ ПРИЗНАЧЕНИЙ ОБРАЗ"
              : "✨ ТВІЙ ПОТОЧНИЙ ВИБІР"}
          </span>
          <p className="survey-package-saved">
            {currentlyActivePackage.tshirt.name} ({currentlyActivePackage.tshirt.color}) +{" "}
            {currentlyActivePackage.tote.name} ({currentlyActivePackage.tote.color})
          </p>
        </div>
      )}

      {packagesLoading && packagesList.length === 0 ? (
        <p className="survey-subtitle" style={{ textAlign: "center", padding: "40px 0" }}>
          Завантаження доступних сетів...
        </p>
      ) : (
        <section className="survey-packages">
          {packagesList.map((pack) => {
            const isAssigned = pack.id === assignedPackageId;
            const isCardSelected = selectedId === pack.id || (!selectedId && isAssigned);

            const teePhoto =
              clothingPhotoSrc(pack.tshirt) || pack.tshirt?.photo;
            const totePhoto =
              clothingPhotoSrc(pack.tote) || pack.tote?.photo;

            return (
              <div
                key={pack.id}
                className={`survey-package-card${isCardSelected ? " is-selected" : ""}${
                  isAssigned ? " is-assigned" : ""
                }${isConfirmed && !isAssigned ? " is-disabled" : ""}`}
                onClick={() => {
                  if (!isConfirmed) {
                    setSelectedId(pack.id);
                  }
                }}
              >
                <span className="survey-package-discount">
                  −{pack.discountPercent || SURVEY_DISCOUNT_PERCENT}%
                </span>

                {isAssigned && (
                  <span className="survey-package-assigned-badge">
                    {isConfirmed ? "ЗАКРІПЛЕНО" : "ТВІЙ СЕТ"}
                  </span>
                )}

                <div className="survey-package-mocks">
                  <div
                    className={`survey-mock survey-mock-tee survey-mock--${pack.tshirt.id}`}
                    style={
                      teePhoto
                        ? {
                            backgroundImage: `url(${teePhoto})`,
                            backgroundSize: "contain",
                            backgroundPosition: "center",
                            backgroundRepeat: "no-repeat",
                          }
                        : undefined
                    }
                  >
                    {!teePhoto && <span>Tee</span>}
                  </div>
                  <div
                    className={`survey-mock survey-mock-tote survey-mock--${pack.tote.id}`}
                    style={
                      totePhoto
                        ? {
                            backgroundImage: `url(${totePhoto})`,
                            backgroundSize: "contain",
                            backgroundPosition: "center",
                            backgroundRepeat: "no-repeat",
                          }
                        : undefined
                    }
                  >
                    {!totePhoto && <span>Tote</span>}
                  </div>
                </div>

                <h2 className="survey-package-title">
                  {pack.tshirt.name} + {pack.tote.name}
                </h2>
                <p className="survey-package-meta">
                  {pack.tshirt.color} · {pack.tote.color}
                </p>
                <p className="survey-package-price">
                  <span className="survey-package-price-old">
                    {pack.price} грн
                  </span>
                  <span>{pack.discountedPrice} грн</span>
                </p>
              </div>
            );
          })}
        </section>
      )}

      <div className="survey-actions">
        <button
          type="button"
          className="survey-btn-catalog"
          onClick={() => navigate("/")}
        >
          ПЕРЕЙТИ В КАТАЛОГ
        </button>

        {currentlyActivePackage && (
          <button
            type="button"
            className="survey-btn-cart"
            onClick={() => handleAddToCart(currentlyActivePackage)}
            disabled={isAddingToCart}
          >
            {isAddingToCart
              ? "ДОДАВАННЯ..."
              : cartSuccess
              ? "ДОДАНО В КОШИК! 🎉"
              : `ДОДАТИ СЕТ У КОШИК 🛍️`}
          </button>
        )}

        {cartSuccess && (
          <button
            type="button"
            className="survey-btn-confirm"
            onClick={() => navigate("/cart")}
          >
            ПЕРЕЙТИ В КОШИК →
          </button>
        )}
      </div>
    </main>
  );
}

export default SurveyRewardPage;
