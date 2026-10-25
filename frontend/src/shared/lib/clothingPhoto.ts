export function optimizePhotoUrl(
  rawUrl: string | null | undefined,
  width = 400,
): string | null {
  if (!rawUrl || typeof rawUrl !== "string") return null;

  if (
    rawUrl.includes("res.cloudinary.com") &&
    rawUrl.includes("/image/upload/") &&
    !rawUrl.includes("/image/upload/f_auto")
  ) {
    return rawUrl.replace(
      "/image/upload/",
      `/image/upload/f_auto,q_auto,w_${width}/`,
    );
  }

  return rawUrl;
}

export function clothingPhotoSrc(
  clothing?: { photo?: string | null; photos?: (string | null)[] | null } | null,
  width = 400,
): string | null {
  const photo = clothing?.photo || clothing?.photos?.[0] || null;
  if (!photo || typeof photo !== "string") return null;
  if (
    photo.startsWith("data:") ||
    photo.startsWith("http") ||
    photo.startsWith("/")
  ) {
    return optimizePhotoUrl(photo, width);
  }
  return `data:image/jpeg;base64,${photo}`;
}
