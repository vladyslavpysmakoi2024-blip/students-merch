const TSHIRTS = [
  { id: "tee-campus", name: "Футболка «Кампус»", color: "Графітова" },
  { id: "tee-vibe", name: "Футболка «Вайб»", color: "Молочна" },
];

const TOTES = [
  { id: "tote-notes", name: "Шопер «Конспект»", color: "Бежевий" },
  { id: "tote-session", name: "Шопер «Сесія»", color: "Чорний" },
  { id: "tote-break", name: "Шопер «Перерва»", color: "Джинсовий" },
];

const PACKAGE_PRICE = 1000;
export const SURVEY_DISCOUNT_PERCENT = 15;

export const SURVEY_PACKAGES = TSHIRTS.flatMap((tshirt) =>
  TOTES.map((tote) => ({
    id: `${tshirt.id}__${tote.id}`,
    tshirt,
    tote,
    price: PACKAGE_PRICE,
    discountPercent: SURVEY_DISCOUNT_PERCENT,
    discountedPrice: Math.round(
      PACKAGE_PRICE * (1 - SURVEY_DISCOUNT_PERCENT / 100),
    ),
  })),
);

const storageKey = (userId) => `surveyRewardPackage:${userId}`;

export const getSavedPackageId = (userId) => {
  if (!userId) return null;
  try {
    return localStorage.getItem(storageKey(userId));
  } catch {
    return null;
  }
};

export const savePackageId = (userId, packageId) => {
  if (!userId || !packageId) return;
  try {
    localStorage.setItem(storageKey(userId), packageId);
  } catch {
    /* placeholder storage only */
  }
};

export const findPackageById = (packageId) =>
  SURVEY_PACKAGES.find((item) => item.id === packageId) || null;
