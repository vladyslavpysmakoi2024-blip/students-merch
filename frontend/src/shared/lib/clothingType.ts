export const isShopper = (type?: string | null): boolean =>
  /шоп+ер/i.test(type || "");

export const shopperTypeLabel = (type?: string | null): string =>
  isShopper(type) ? "Шопери" : type || "";
