export interface SurveyMerchPiece {
  id: string | number;
  name: string;
  color: string;
  photo?: string | null;
  photos?: string[] | null;
}

export interface SurveyPackage {
  id: string;
  tshirt: SurveyMerchPiece;
  tote: SurveyMerchPiece;
  price: number;
  discountPercent: number;
  discountedPrice: number;
}

const TSHIRTS: SurveyMerchPiece[] = [
  { id: "tee-campus", name: "Футболка «Кампус»", color: "Графітова" },
  { id: "tee-vibe", name: "Футболка «Вайб»", color: "Молочна" },
];

const TOTES: SurveyMerchPiece[] = [
  { id: "tote-notes", name: "Шопер «Конспект»", color: "Бежевий" },
  { id: "tote-session", name: "Шопер «Сесія»", color: "Чорний" },
  { id: "tote-break", name: "Шопер «Перерва»", color: "Джинсовий" },
];

const PACKAGE_PRICE = 1000;
export const SURVEY_DISCOUNT_PERCENT = 15;

export const SURVEY_PACKAGES: SurveyPackage[] = TSHIRTS.flatMap((tshirt) =>
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

const storageKey = (userId: number | string) => `surveyRewardPackage:${userId}`;

export const getSavedPackageId = (userId?: number | string | null): string | null => {
  if (!userId) return null;
  try {
    return localStorage.getItem(storageKey(userId));
  } catch {
    return null;
  }
};

export const savePackageId = (
  userId?: number | string | null,
  packageId?: string | null,
): void => {
  if (!userId || !packageId) return;
  try {
    localStorage.setItem(storageKey(userId), packageId);
  } catch {
    /* placeholder storage only */
  }
};

export const findPackageById = (
  packageId?: string | null,
): SurveyPackage | null =>
  SURVEY_PACKAGES.find((item) => item.id === packageId) || null;
