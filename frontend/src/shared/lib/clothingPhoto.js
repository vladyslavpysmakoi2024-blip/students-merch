export function clothingPhotoSrc(clothing) {
  const photo = clothing?.photo || clothing?.photos?.[0] || null;
  if (!photo || typeof photo !== "string") return null;
  if (
    photo.startsWith("data:") ||
    photo.startsWith("http") ||
    photo.startsWith("/")
  ) {
    return photo;
  }
  return `data:image/jpeg;base64,${photo}`;
}
