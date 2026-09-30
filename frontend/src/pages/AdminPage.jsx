import { useState } from "react";
import { useIsMutating } from "@tanstack/react-query";
import { useCurrentUser, useLogin, useLogout } from "../features/auth/useAuth";
import {
  adminKeys,
  useAdminClothing,
  useAdminOrders,
  useAdminPromos,
  useBulkUpdateClothes,
  useCreateClothes,
  useDeleteClothes,
  useDeletePromo,
  useSavePromo,
  useUpdateClothing,
  useUploadClothingPhoto,
} from "../features/admin/useAdmin";
import { clothingPhotoSrc } from "../shared/lib/clothingPhoto";

const TABS = [
  { id: "clothing", label: "Товари" },
  { id: "promo", label: "Промокоди" },
  { id: "orders", label: "Замовлення" },
];

const PAID_STATUS = "COMPLETED";

const ORDER_STATUS_LABELS = {
  CREATED: "Очікує оплати",
  COMPLETED: "Оплачено",
  FAILED: "Оплата не пройшла",
};

const EMPTY_CLOTHING = {
  name: "",
  type: "",
  color: "",
  size: "",
  composition: "",
  price: "",
  quantity: "",
  photos: [""],
};

const NEW_SIZES = ["S", "M", "L", "XL"].map((size) => ({
  size,
  quantity: "",
}));

const SIZE_ORDER = ["XS", "S", "M", "L", "XL", "XXL"];

const MAX_PHOTO_SIZE = 5 * 1024 * 1024;

const EMPTY_PROMO = {
  promo: "",
  discount_percent: "",
  date_start: "",
  date_end: "",
};

const errorText = (error) => {
  const detail = error?.response?.data?.detail;
  return typeof detail === "string"
    ? detail
    : "Не вдалося зберегти. Перевір правильність полів";
};

const toClothingForm = (item) => ({
  name: item.name || "",
  type: item.type || "",
  color: item.color || "",
  size: item.size || "",
  composition: item.composition || "",
  price: item.price ?? "",
  quantity: item.quantity ?? "",
  photos: item.photos?.length ? item.photos : [""],
});

const toClothingPayload = (form) => ({
  name: form.name.trim() || null,
  type: form.type.trim() || null,
  color: form.color.trim() || null,
  size: form.size.trim() || null,
  composition: form.composition.trim() || null,
  price: form.price,
  quantity: form.quantity === "" ? null : Number(form.quantity),
  photos: form.photos,
});

const toBulkPayload = (ids, form) => {
  const payload = { ids };
  ["name", "type", "color", "composition"].forEach((field) => {
    if (form[field].trim()) payload[field] = form[field].trim();
  });
  if (form.price !== "") payload.price = form.price;
  if (form.quantity !== "") payload.quantity = Number(form.quantity);
  const photos = form.photos.filter((photo) => photo.trim());
  if (photos.length) payload.photos = photos;
  return payload;
};

const sizeRank = (size) => {
  const index = SIZE_ORDER.indexOf((size || "").toUpperCase());
  return index === -1 ? SIZE_ORDER.length : index;
};

const compareText = (a, b) => (a || "").localeCompare(b || "", "uk");

const CLOTHING_COLUMNS = [
  { key: "id", label: "ID", compare: (a, b) => a.id - b.id },
  {
    key: "name",
    label: "Назва",
    compare: (a, b) => compareText(a.name, b.name),
  },
  { key: "type", label: "Тип", compare: (a, b) => compareText(a.type, b.type) },
  {
    key: "color",
    label: "Колір",
    compare: (a, b) => compareText(a.color_name, b.color_name),
  },
  {
    key: "size",
    label: "Розмір",
    compare: (a, b) => sizeRank(a.size) - sizeRank(b.size),
  },
  {
    key: "price",
    label: "Ціна",
    compare: (a, b) => Number(a.price) - Number(b.price),
  },
  {
    key: "quantity",
    label: "Кількість",
    compare: (a, b) => (a.quantity ?? 0) - (b.quantity ?? 0),
  },
];

const compareClothes = (a, b) =>
  compareText(a.name, b.name) ||
  compareText(a.color_name, b.color_name) ||
  sizeRank(a.size) - sizeRank(b.size) ||
  a.id - b.id;

function AdminLogin() {
  const [form, setForm] = useState({ email: "", password: "" });
  const [error, setError] = useState("");
  const { mutate: login, isPending } = useLogin();

  const handleChange = (e) =>
    setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = (e) => {
    e.preventDefault();
    if (isPending) return;
    setError("");
    login(form, {
      onError: () => setError("Неправильний email або пароль"),
    });
  };

  return (
    <div className="admin-page admin-page--center">
      <form className="admin-card admin-login" onSubmit={handleSubmit}>
        <h1 className="admin-title">Вхід для менеджера</h1>
        <label className="admin-field">
          Email
          <input
            type="email"
            name="email"
            value={form.email}
            onChange={handleChange}
            required
          />
        </label>
        <label className="admin-field">
          Пароль
          <input
            type="password"
            name="password"
            value={form.password}
            onChange={handleChange}
            required
          />
        </label>
        {error && <p className="admin-error">{error}</p>}
        <button className="admin-btn" type="submit" disabled={isPending}>
          Увійти
        </button>
      </form>
    </div>
  );
}

function PhotoEditor({ photos, onChange, onError }) {
  const { mutateAsync: uploadPhoto } = useUploadClothingPhoto();
  const isUploading = useIsMutating({ mutationKey: adminKeys.photoUpload }) > 0;

  const handleUpload = (e) => {
    const files = [...e.target.files];
    e.target.value = "";
    files.forEach((file) => {
      if (file.size > MAX_PHOTO_SIZE) {
        onError(`${file.name}: максимальний розмір фото — 5 МБ`);
        return;
      }
      uploadPhoto(file)
        .then(({ url }) =>
          onChange((current) => [...current.filter(Boolean), url]),
        )
        .catch((err) => onError(errorText(err)));
    });
  };

  return (
    <div className="admin-field">
      Фото
      {photos.map((photo, index) => (
        <div className="admin-photo-row" key={index}>
          {clothingPhotoSrc({ photo }) ? (
            <img src={clothingPhotoSrc({ photo })} alt="" />
          ) : (
            <div className="admin-photo-empty" />
          )}
          <input
            value={photo}
            onChange={(e) =>
              onChange((current) =>
                current.map((item, i) => (i === index ? e.target.value : item)),
              )
            }
            placeholder="https://..."
          />
          <button
            className="admin-btn admin-btn--ghost"
            type="button"
            onClick={() =>
              onChange((current) => current.filter((_, i) => i !== index))
            }
          >
            Прибрати
          </button>
        </div>
      ))}
      <div className="admin-actions">
        <label className="admin-btn admin-btn--small">
          {isUploading ? "Завантаження..." : "Завантажити з комп'ютера"}
          <input
            type="file"
            accept="image/jpeg,image/png,image/webp"
            multiple
            hidden
            onChange={handleUpload}
            disabled={isUploading}
          />
        </label>
        <button
          className="admin-btn admin-btn--ghost admin-btn--small"
          type="button"
          onClick={() => onChange((current) => [...current, ""])}
        >
          + Додати посиланням
        </button>
      </div>
    </div>
  );
}

function ClothingTab() {
  const { clothes, isLoading, isError } = useAdminClothing();
  const { mutate: updateClothing, isPending: isUpdating } = useUpdateClothing();
  const { mutate: createClothes, isPending: isCreating } = useCreateClothes();
  const { mutate: bulkUpdateClothes, isPending: isBulkUpdating } =
    useBulkUpdateClothes();
  const { mutate: deleteClothes, isPending: isDeleting } = useDeleteClothes();
  const isUploading = useIsMutating({ mutationKey: adminKeys.photoUpload }) > 0;
  const [search, setSearch] = useState("");
  const [selectedIds, setSelectedIds] = useState([]);
  const [sort, setSort] = useState(null);
  const [form, setForm] = useState(null);
  const [error, setError] = useState("");

  const isSaving = isUpdating || isCreating || isBulkUpdating || isUploading;

  const totalUnits = clothes.reduce(
    (sum, item) => sum + (item.quantity || 0),
    0,
  );
  const outOfStock = clothes.filter((item) => !item.quantity).length;

  const words = search.trim().toLowerCase().split(/\s+/).filter(Boolean);
  const visibleClothes = clothes
    .filter((item) =>
      words.every((word) =>
        [
          item.name,
          item.type,
          item.size,
          item.color_name,
          String(item.id),
        ].some((value) => value?.toLowerCase().includes(word)),
      ),
    )
    .sort(
      (a, b) =>
        (sort
          ? sort.direction *
            CLOTHING_COLUMNS.find((column) => column.key === sort.key).compare(
              a,
              b,
            )
          : 0) || compareClothes(a, b),
    );
  const visibleIds = visibleClothes.map((item) => item.id);
  const allVisibleSelected =
    visibleIds.length > 0 && visibleIds.every((id) => selectedIds.includes(id));

  const toggleSort = (key) =>
    setSort((prev) =>
      prev?.key === key
        ? { key, direction: -prev.direction }
        : { key, direction: 1 },
    );

  const handleDelete = (ids) => {
    if (isDeleting) return;
    if (!window.confirm(`Видалити товари (${ids.length} шт.)? Це незворотно.`))
      return;
    deleteClothes(ids, {
      onSuccess: () =>
        setSelectedIds((current) => current.filter((id) => !ids.includes(id))),
      onError: (err) => window.alert(errorText(err)),
    });
  };

  const toggleSelected = (id) =>
    setSelectedIds((ids) =>
      ids.includes(id) ? ids.filter((item) => item !== id) : [...ids, id],
    );

  const toggleAllVisible = () =>
    setSelectedIds((ids) =>
      allVisibleSelected
        ? ids.filter((id) => !visibleIds.includes(id))
        : [...new Set([...ids, ...visibleIds])],
    );

  const openForm = (mode, values, id = null) => {
    setError("");
    setForm({ mode, id, values });
  };

  const updateField = (field, value) =>
    setForm((prev) => ({
      ...prev,
      values: { ...prev.values, [field]: value },
    }));

  const setPhotos = (update) =>
    setForm(
      (prev) =>
        prev && {
          ...prev,
          values: { ...prev.values, photos: update(prev.values.photos) },
        },
    );

  const updateSizeRow = (index, field, value) =>
    updateField(
      "sizes",
      form.values.sizes.map((row, i) =>
        i === index ? { ...row, [field]: value } : row,
      ),
    );

  const handleSubmit = (e) => {
    e.preventDefault();
    if (isSaving) return;
    setError("");
    const callbacks = {
      onSuccess: () => setForm(null),
      onError: (err) => setError(errorText(err)),
    };

    if (form.mode === "edit") {
      updateClothing(
        { id: form.id, data: toClothingPayload(form.values) },
        callbacks,
      );
      return;
    }

    if (form.mode === "create") {
      const rows = form.values.sizes.filter((row) => row.size.trim());
      if (!rows.length) {
        setError("Додай хоча б один розмір");
        return;
      }
      createClothes(
        rows.map((row) =>
          toClothingPayload({
            ...form.values,
            size: row.size,
            quantity: row.quantity,
          }),
        ),
        callbacks,
      );
      return;
    }

    const payload = toBulkPayload(selectedIds, form.values);
    if (Object.keys(payload).length === 1) {
      setError("Заповни хоча б одне поле");
      return;
    }
    bulkUpdateClothes(payload, {
      onSuccess: () => {
        setForm(null);
        setSelectedIds([]);
      },
      onError: callbacks.onError,
    });
  };

  if (isLoading) return <p className="admin-muted">Завантаження...</p>;
  if (isError)
    return <p className="admin-error">Не вдалося завантажити товари.</p>;

  return (
    <>
      <div className="admin-stats">
        <div className="admin-stat">
          <span>{clothes.length}</span>Позицій
        </div>
        <div className="admin-stat">
          <span>{totalUnits}</span>Одиниць на складі
        </div>
        <div className="admin-stat admin-stat--warning">
          <span>{outOfStock}</span>Закінчились
        </div>
      </div>

      {form && (
        <form className="admin-card admin-form" onSubmit={handleSubmit}>
          <h2 className="admin-subtitle">
            {form.mode === "edit" && `Товар #${form.id}`}
            {form.mode === "create" && "Новий товар"}
            {form.mode === "bulk" &&
              `Редагування вибраних: ${selectedIds.length} шт.`}
          </h2>
          {form.mode === "bulk" && (
            <p className="admin-muted">
              Порожні поля не змінюються. Якщо додати фото — вони замінять фото
              в усіх вибраних товарах.
            </p>
          )}
          {form.mode === "create" && (
            <p className="admin-muted">
              Для кожного розміру створиться окрема позиція з однаковими назвою,
              кольором, ціною та фото.
            </p>
          )}
          <div className="admin-form-grid">
            <label className="admin-field">
              Назва
              <input
                value={form.values.name}
                onChange={(e) => updateField("name", e.target.value)}
              />
            </label>
            <label className="admin-field">
              Тип
              <input
                value={form.values.type}
                onChange={(e) => updateField("type", e.target.value)}
              />
            </label>
            <label className="admin-field">
              Колір (HEX)
              <div className="admin-color">
                <input
                  value={form.values.color}
                  onChange={(e) => updateField("color", e.target.value)}
                  placeholder="#FFFFFF"
                />
                <input
                  type="color"
                  value={form.values.color || "#000000"}
                  onChange={(e) => updateField("color", e.target.value)}
                />
              </div>
            </label>
            <label className="admin-field">
              Склад
              <input
                value={form.values.composition}
                onChange={(e) => updateField("composition", e.target.value)}
              />
            </label>
            <label className="admin-field">
              Ціна, ₴
              <input
                type="number"
                min="0.01"
                step="0.01"
                value={form.values.price}
                onChange={(e) => updateField("price", e.target.value)}
                required={form.mode !== "bulk"}
              />
            </label>
            {form.mode === "edit" && (
              <label className="admin-field">
                Розмір
                <input
                  value={form.values.size}
                  onChange={(e) => updateField("size", e.target.value)}
                />
              </label>
            )}
            {form.mode !== "create" && (
              <label className="admin-field">
                Кількість
                <input
                  type="number"
                  min="0"
                  step="1"
                  value={form.values.quantity}
                  onChange={(e) => updateField("quantity", e.target.value)}
                />
              </label>
            )}
          </div>

          {form.mode === "create" && (
            <div className="admin-field admin-sizes">
              Розміри та кількість
              {form.values.sizes.map((row, index) => (
                <div className="admin-size-row" key={index}>
                  <input
                    value={row.size}
                    onChange={(e) =>
                      updateSizeRow(index, "size", e.target.value)
                    }
                    placeholder="Розмір"
                  />
                  <input
                    type="number"
                    min="0"
                    step="1"
                    value={row.quantity}
                    onChange={(e) =>
                      updateSizeRow(index, "quantity", e.target.value)
                    }
                    placeholder="Кількість"
                  />
                  <button
                    className="admin-btn admin-btn--ghost"
                    type="button"
                    onClick={() =>
                      updateField(
                        "sizes",
                        form.values.sizes.filter((_, i) => i !== index),
                      )
                    }
                  >
                    Прибрати
                  </button>
                </div>
              ))}
              <button
                className="admin-btn admin-btn--ghost admin-btn--small"
                type="button"
                onClick={() =>
                  updateField("sizes", [
                    ...form.values.sizes,
                    { size: "", quantity: "" },
                  ])
                }
              >
                + Додати розмір
              </button>
            </div>
          )}

          <PhotoEditor
            photos={form.values.photos}
            onChange={setPhotos}
            onError={setError}
          />

          {error && <p className="admin-error">{error}</p>}
          <div className="admin-actions">
            <button className="admin-btn" type="submit" disabled={isSaving}>
              Зберегти
            </button>
            <button
              className="admin-btn admin-btn--ghost"
              type="button"
              onClick={() => setForm(null)}
            >
              Скасувати
            </button>
          </div>
        </form>
      )}

      <div className="admin-toolbar">
        <input
          className="admin-search"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Пошук: назва, тип, колір, розмір або ID"
        />
        <button
          className="admin-btn"
          type="button"
          onClick={() =>
            openForm("create", { ...EMPTY_CLOTHING, sizes: NEW_SIZES })
          }
        >
          + Додати товар
        </button>
        {selectedIds.length > 0 && (
          <>
            <button
              className="admin-btn"
              type="button"
              onClick={() => openForm("bulk", EMPTY_CLOTHING)}
            >
              Редагувати вибрані ({selectedIds.length})
            </button>
            <button
              className="admin-btn admin-btn--danger"
              type="button"
              onClick={() => handleDelete(selectedIds)}
              disabled={isDeleting}
            >
              Видалити вибрані ({selectedIds.length})
            </button>
            <button
              className="admin-btn admin-btn--ghost"
              type="button"
              onClick={() => setSelectedIds([])}
            >
              Зняти виділення
            </button>
          </>
        )}
      </div>

      <div className="admin-table-wrap">
        <table className="admin-table">
          <thead>
            <tr>
              <th>
                <input
                  type="checkbox"
                  checked={allVisibleSelected}
                  onChange={toggleAllVisible}
                  aria-label="Вибрати всі"
                />
              </th>
              <th>Фото</th>
              {CLOTHING_COLUMNS.map((column) => (
                <th key={column.key}>
                  <button
                    className="admin-sort"
                    type="button"
                    onClick={() => toggleSort(column.key)}
                  >
                    {column.label}
                    {sort?.key === column.key &&
                      (sort.direction === 1 ? " ▲" : " ▼")}
                  </button>
                </th>
              ))}
              <th />
            </tr>
          </thead>
          <tbody>
            {visibleClothes.map((item) => (
              <tr
                key={item.id}
                className={
                  selectedIds.includes(item.id) ? "admin-row--selected" : ""
                }
              >
                <td>
                  <input
                    type="checkbox"
                    checked={selectedIds.includes(item.id)}
                    onChange={() => toggleSelected(item.id)}
                    aria-label={`Вибрати товар ${item.id}`}
                  />
                </td>
                <td>
                  {clothingPhotoSrc(item) ? (
                    <img
                      className="admin-thumb"
                      src={clothingPhotoSrc(item)}
                      alt=""
                    />
                  ) : (
                    <div className="admin-thumb admin-photo-empty" />
                  )}
                </td>
                <td>{item.id}</td>
                <td>{item.name || "—"}</td>
                <td>{item.type || "—"}</td>
                <td>
                  {item.color ? (
                    <span className="admin-swatch-cell">
                      <span
                        className="admin-swatch"
                        style={{ background: item.color }}
                      />
                      {item.color_name || item.color}
                    </span>
                  ) : (
                    "—"
                  )}
                </td>
                <td>{item.size || "—"}</td>
                <td>{item.price} ₴</td>
                <td className={item.quantity ? "" : "admin-danger"}>
                  {item.quantity ?? 0}
                </td>
                <td className="admin-row-actions">
                  <button
                    className="admin-btn admin-btn--small"
                    type="button"
                    onClick={() =>
                      openForm("edit", toClothingForm(item), item.id)
                    }
                  >
                    Редагувати
                  </button>
                  <button
                    className="admin-btn admin-btn--small admin-btn--danger"
                    type="button"
                    onClick={() => handleDelete([item.id])}
                    disabled={isDeleting}
                  >
                    Видалити
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {visibleClothes.length === 0 && (
          <p className="admin-muted">Нічого не знайдено.</p>
        )}
      </div>
    </>
  );
}

function PromoTab() {
  const { promos, isLoading, isError } = useAdminPromos();
  const { mutate: savePromo, isPending } = useSavePromo();
  const { mutate: removePromo } = useDeletePromo();
  const [editing, setEditing] = useState(null);
  const [error, setError] = useState("");

  const today = new Date().toISOString().slice(0, 10);

  const openForm = (id, form) => {
    setError("");
    setEditing({ id, form });
  };

  const updateForm = (field, value) =>
    setEditing({ ...editing, form: { ...editing.form, [field]: value } });

  const handleSubmit = (e) => {
    e.preventDefault();
    if (isPending) return;
    if (editing.form.date_end < editing.form.date_start) {
      setError("Дата завершення не може бути раніше дати початку");
      return;
    }
    setError("");
    savePromo(
      { id: editing.id, data: editing.form },
      {
        onSuccess: () => setEditing(null),
        onError: (err) => setError(errorText(err)),
      },
    );
  };

  const handleDelete = (promo) => {
    if (!window.confirm(`Видалити промокод ${promo.promo}?`)) return;
    removePromo(promo.id, {
      onError: (err) => window.alert(errorText(err)),
    });
  };

  const promoState = (promo) => {
    if (promo.date_end < today) return "Завершено";
    if (promo.date_start > today) return "Заплановано";
    return "Діє";
  };

  if (isLoading) return <p className="admin-muted">Завантаження...</p>;
  if (isError)
    return <p className="admin-error">Не вдалося завантажити промокоди.</p>;

  return (
    <>
      {editing && (
        <form className="admin-card admin-form" onSubmit={handleSubmit}>
          <h2 className="admin-subtitle">
            {editing.id ? "Редагування промокоду" : "Новий промокод"}
          </h2>
          <div className="admin-form-grid">
            <label className="admin-field">
              Код
              <input
                value={editing.form.promo}
                onChange={(e) => updateForm("promo", e.target.value)}
                maxLength={50}
                required
              />
            </label>
            <label className="admin-field">
              Знижка, %
              <input
                type="number"
                min="0.01"
                max="100"
                step="0.01"
                value={editing.form.discount_percent}
                onChange={(e) => updateForm("discount_percent", e.target.value)}
                required
              />
            </label>
            <label className="admin-field">
              Діє з
              <input
                type="date"
                value={editing.form.date_start}
                onChange={(e) => updateForm("date_start", e.target.value)}
                required
              />
            </label>
            <label className="admin-field">
              Діє до
              <input
                type="date"
                value={editing.form.date_end}
                onChange={(e) => updateForm("date_end", e.target.value)}
                required
              />
            </label>
          </div>
          {error && <p className="admin-error">{error}</p>}
          <div className="admin-actions">
            <button className="admin-btn" type="submit" disabled={isPending}>
              Зберегти
            </button>
            <button
              className="admin-btn admin-btn--ghost"
              type="button"
              onClick={() => setEditing(null)}
            >
              Скасувати
            </button>
          </div>
        </form>
      )}

      <div className="admin-toolbar">
        <button
          className="admin-btn"
          type="button"
          onClick={() => openForm(null, EMPTY_PROMO)}
        >
          + Додати промокод
        </button>
      </div>

      <div className="admin-table-wrap">
        <table className="admin-table">
          <thead>
            <tr>
              <th>Код</th>
              <th>Знижка</th>
              <th>Діє з</th>
              <th>Діє до</th>
              <th>Стан</th>
              <th />
            </tr>
          </thead>
          <tbody>
            {promos.map((promo) => (
              <tr key={promo.id}>
                <td>{promo.promo}</td>
                <td>{promo.discount_percent}%</td>
                <td>{promo.date_start}</td>
                <td>{promo.date_end}</td>
                <td>{promoState(promo)}</td>
                <td className="admin-row-actions">
                  <button
                    className="admin-btn admin-btn--small"
                    type="button"
                    onClick={() =>
                      openForm(promo.id, {
                        promo: promo.promo,
                        discount_percent: promo.discount_percent,
                        date_start: promo.date_start,
                        date_end: promo.date_end,
                      })
                    }
                  >
                    Редагувати
                  </button>
                  <button
                    className="admin-btn admin-btn--small admin-btn--danger"
                    type="button"
                    onClick={() => handleDelete(promo)}
                  >
                    Видалити
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {promos.length === 0 && (
          <p className="admin-muted">Промокодів ще немає.</p>
        )}
      </div>
    </>
  );
}

function OrdersTab() {
  const { orders, isLoading, isError } = useAdminOrders();
  const [filter, setFilter] = useState("all");

  const paidOrders = orders.filter((order) => order.status === PAID_STATUS);
  const paidSum = paidOrders.reduce(
    (sum, order) => sum + Number(order.price),
    0,
  );
  const visibleOrders = orders.filter((order) => {
    if (filter === "paid") return order.status === PAID_STATUS;
    if (filter === "unpaid") return order.status !== PAID_STATUS;
    return true;
  });

  if (isLoading) return <p className="admin-muted">Завантаження...</p>;
  if (isError)
    return <p className="admin-error">Не вдалося завантажити замовлення.</p>;

  return (
    <>
      <div className="admin-stats">
        <div className="admin-stat">
          <span>{orders.length}</span>Усього замовлень
        </div>
        <div className="admin-stat admin-stat--success">
          <span>{paidOrders.length}</span>Оплачено
        </div>
        <div className="admin-stat admin-stat--warning">
          <span>{orders.length - paidOrders.length}</span>Не оплачено
        </div>
        <div className="admin-stat">
          <span>{paidSum.toFixed(2)} ₴</span>Сума оплачених
        </div>
      </div>

      <div className="admin-toolbar">
        <select
          className="admin-search"
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
        >
          <option value="all">Усі замовлення</option>
          <option value="paid">Оплачені</option>
          <option value="unpaid">Не оплачені</option>
        </select>
      </div>

      <div className="admin-table-wrap">
        <table className="admin-table">
          <thead>
            <tr>
              <th>№</th>
              <th>Дата</th>
              <th>Покупець</th>
              <th>Товари</th>
              <th>Доставка</th>
              <th>Сума</th>
              <th>Статус</th>
            </tr>
          </thead>
          <tbody>
            {visibleOrders.map((order) => (
              <tr key={order.id}>
                <td>{order.id}</td>
                <td>
                  {order.date
                    ? new Date(order.date).toLocaleString("uk-UA")
                    : "—"}
                </td>
                <td>
                  {order.user ? (
                    <>
                      {[order.user.first_name, order.user.last_name]
                        .filter(Boolean)
                        .join(" ")}
                      <div className="admin-muted">{order.user.email}</div>
                      <div className="admin-muted">
                        {order.user.phone_number}
                      </div>
                    </>
                  ) : (
                    "—"
                  )}
                </td>
                <td>
                  {order.order_content
                    .map((content) => content.clothing.name)
                    .join(", ") || "—"}
                </td>
                <td>
                  {[
                    order.delivery_company,
                    order.delivery_type,
                    order.postal_number,
                  ]
                    .filter(Boolean)
                    .join(", ") || "—"}
                </td>
                <td>{order.price} ₴</td>
                <td>
                  <span
                    className={`admin-badge ${
                      order.status === PAID_STATUS ? "admin-badge--paid" : ""
                    }`}
                  >
                    {ORDER_STATUS_LABELS[order.status] || order.status}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {visibleOrders.length === 0 && (
          <p className="admin-muted">Замовлень немає.</p>
        )}
      </div>
    </>
  );
}

function AdminPage() {
  const { user, isLoading } = useCurrentUser();
  const { mutate: logout } = useLogout();
  const [tab, setTab] = useState("clothing");

  if (isLoading) {
    return (
      <div className="admin-page admin-page--center">
        <p className="admin-muted">Завантаження...</p>
      </div>
    );
  }

  if (!user) return <AdminLogin />;

  if (!user.is_admin) {
    return (
      <div className="admin-page admin-page--center">
        <div className="admin-card admin-login">
          <h1 className="admin-title">Немає доступу</h1>
          <p className="admin-muted">
            Акаунт {user.email} не має прав адміністратора.
          </p>
          <button className="admin-btn" type="button" onClick={() => logout()}>
            Увійти з іншого акаунта
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="admin-page">
      <header className="admin-header">
        <h1 className="admin-title">Панель менеджера</h1>
        <div className="admin-header-user">
          <span className="admin-muted">{user.email}</span>
          <button
            className="admin-btn admin-btn--ghost admin-btn--small"
            type="button"
            onClick={() => logout()}
          >
            Вийти
          </button>
        </div>
      </header>

      <nav className="admin-tabs">
        {TABS.map((item) => (
          <button
            key={item.id}
            className={`admin-tab ${tab === item.id ? "admin-tab--active" : ""}`}
            type="button"
            onClick={() => setTab(item.id)}
          >
            {item.label}
          </button>
        ))}
      </nav>

      {tab === "clothing" && <ClothingTab />}
      {tab === "promo" && <PromoTab />}
      {tab === "orders" && <OrdersTab />}
    </div>
  );
}

export default AdminPage;
