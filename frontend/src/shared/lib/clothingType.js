export const isShopper = (type) => /шоп+ер/i.test(type || "");

export const shopperTypeLabel = (type) => (isShopper(type) ? "Шопери" : type);
