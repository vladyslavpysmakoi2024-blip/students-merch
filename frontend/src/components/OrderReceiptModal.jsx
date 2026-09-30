import React from "react";
import {
  FiCheckCircle,
  FiExternalLink,
  FiPrinter,
  FiShoppingBag,
  FiX,
} from "react-icons/fi";
import { useOrderReceipt } from "../features/profile/useProfile";

export const OrderReceiptModal = ({ orderId, onClose }) => {
  const { receipt, isLoading, isError, error } = useOrderReceipt(
    orderId,
    Boolean(orderId),
  );

  const handlePrint = () => {
    window.print();
  };

  const formatDate = (isoString) => {
    if (!isoString) return "—";
    try {
      const d = new Date(isoString);
      return d.toLocaleString("uk-UA", {
        day: "2-digit",
        month: "2-digit",
        year: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      });
    } catch {
      return isoString;
    }
  };

  const formatPrice = (val) => {
    if (val === undefined || val === null) return "0 ₴";
    return `${Number(val).toLocaleString("uk-UA")} ₴`;
  };

  if (!orderId) return null;

  return (
    <div className="receipt-modal-backdrop" onClick={onClose}>
      <div
        className="receipt-modal-card"
        onClick={(e) => e.stopPropagation()}
        role="dialog"
        aria-modal="true"
        aria-labelledby="receipt-title"
      >
        <button
          className="receipt-modal-close-btn no-print"
          onClick={onClose}
          aria-label="Закрити"
        >
          <FiX size={22} />
        </button>

        {isLoading ? (
          <div className="receipt-loading-state">
            <div className="receipt-spinner"></div>
            <p>Завантаження чека замовлення...</p>
          </div>
        ) : isError ? (
          <div className="receipt-error-state">
            <p className="receipt-error-msg">
              {error?.response?.data?.detail ||
                "Не вдалося завантажити чек. Переконайтеся, що замовлення успішно оплачене."}
            </p>
            <button className="receipt-action-btn close-btn" onClick={onClose}>
              Закрити
            </button>
          </div>
        ) : receipt ? (
          <>
            {/* Action Bar (Not visible in Print) */}
            <div className="receipt-action-bar no-print">
              <div className="receipt-action-bar-left">
                <span className="receipt-status-badge">
                  <FiCheckCircle size={15} /> Оплачено
                </span>
                <span className="receipt-number-tag">
                  {receipt.receipt_number || `№ ${receipt.order_id}`}
                </span>
              </div>
              <div className="receipt-action-bar-right">
                {receipt.monobank_receipt_url && (
                  <a
                    href={receipt.monobank_receipt_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="receipt-mono-btn"
                  >
                    <FiExternalLink size={15} /> Чек Monobank
                  </a>
                )}
                <button
                  className="receipt-print-btn"
                  onClick={handlePrint}
                  title="Роздрукувати або зберегти як PDF"
                >
                  <FiPrinter size={16} /> Друк / PDF
                </button>
              </div>
            </div>

            {/* Printable Receipt Sheet */}
            <div className="receipt-sheet" id="printable-receipt">
              {/* Receipt Header */}
              <div className="receipt-header">
                <div className="receipt-logo">
                  <span className="receipt-logo-bold">STUDENTS</span>
                  <span className="receipt-logo-light">MERCH</span>
                </div>
                <div className="receipt-title-wrapper">
                  <h2 id="receipt-title" className="receipt-title">
                    ТОВАРНИЙ ЧЕК
                  </h2>
                  <div className="receipt-chk-num">{receipt.receipt_number}</div>
                </div>
              </div>

              <div className="receipt-divider-dashed" />

              {/* Store & Order Meta */}
              <div className="receipt-meta-grid">
                <div className="receipt-meta-col">
                  <span className="receipt-meta-label">Продавець:</span>
                  <span className="receipt-meta-value font-medium">
                    {receipt.store_name}
                  </span>
                  <span className="receipt-meta-sub">
                    {receipt.store_address}
                  </span>
                </div>
                <div className="receipt-meta-col text-right">
                  <span className="receipt-meta-label">Дата оплати:</span>
                  <span className="receipt-meta-value">
                    {formatDate(receipt.created_at)}
                  </span>
                  <span className="receipt-meta-label mt-1">Оплата:</span>
                  <span className="receipt-meta-value font-medium text-success">
                    {receipt.payment_method}
                  </span>
                </div>
              </div>

              {/* Customer & Delivery */}
              <div className="receipt-customer-box">
                <div className="receipt-customer-row">
                  <span className="receipt-meta-label">Покупець:</span>
                  <span className="receipt-meta-value">
                    {receipt.customer?.name || "Клієнт"}
                    {receipt.customer?.phone
                      ? ` (${receipt.customer.phone})`
                      : ""}
                  </span>
                </div>
                {(receipt.delivery_company || receipt.customer?.city) && (
                  <div className="receipt-customer-row">
                    <span className="receipt-meta-label">Доставка:</span>
                    <span className="receipt-meta-value">
                      {[
                        receipt.delivery_company,
                        receipt.customer?.city,
                        receipt.customer?.street &&
                          `вул. ${receipt.customer.street}`,
                        receipt.customer?.house_number &&
                          `буд. ${receipt.customer.house_number}`,
                        receipt.postal_number &&
                          `Відділення/Поштомат №${receipt.postal_number}`,
                      ]
                        .filter(Boolean)
                        .join(", ")}
                    </span>
                  </div>
                )}
                {receipt.invoice_id && (
                  <div className="receipt-customer-row receipt-invoice-row">
                    <span className="receipt-meta-label">ID транзакції:</span>
                    <span className="receipt-meta-value receipt-mono-code">
                      {receipt.invoice_id}
                    </span>
                  </div>
                )}
              </div>

              <div className="receipt-divider" />

              {/* Items Table */}
              <div className="receipt-items-table-wrapper">
                <table className="receipt-items-table">
                  <thead>
                    <tr>
                      <th className="th-item">Товар</th>
                      <th className="th-type">Тип / Колір</th>
                      <th className="th-qty text-center">К-сть</th>
                      <th className="th-price text-right">Ціна</th>
                      <th className="th-total text-right">Сума</th>
                    </tr>
                  </thead>
                  <tbody>
                    {receipt.items && receipt.items.length > 0 ? (
                      receipt.items.map((item, idx) => (
                        <tr key={idx}>
                          <td className="td-item">
                            <div className="receipt-item-name-cell">
                              {item.photo && (
                                <img
                                  src={item.photo}
                                  alt={item.name}
                                  className="receipt-item-thumb no-print"
                                />
                              )}
                              <span>{item.name}</span>
                            </div>
                          </td>
                          <td className="td-type">
                            {[item.type, item.size && `Розмір: ${item.size}`]
                              .filter(Boolean)
                              .join(" · ") || "—"}
                          </td>
                          <td className="td-qty text-center">
                            {item.quantity || 1}
                          </td>
                          <td className="td-price text-right">
                            {formatPrice(item.price)}
                          </td>
                          <td className="td-total text-right font-medium">
                            {formatPrice(item.total || item.price)}
                          </td>
                        </tr>
                      ))
                    ) : (
                      <tr>
                        <td colSpan="5" className="text-center py-3">
                          Товари відсутні
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>

              <div className="receipt-divider" />

              {/* Financial Totals */}
              <div className="receipt-totals-section">
                <div className="receipt-totals-row">
                  <span>Підсумок:</span>
                  <span>{formatPrice(receipt.subtotal)}</span>
                </div>
                <div className="receipt-totals-row font-bold receipt-grand-total">
                  <span>ВСЬОГО СПЛАЧЕНО:</span>
                  <span>{formatPrice(receipt.total_amount)}</span>
                </div>
              </div>

              <div className="receipt-divider-dashed" />

              {/* Receipt Footer */}
              <div className="receipt-footer">
                <div className="receipt-footer-thanks">
                  <FiShoppingBag className="inline-icon" /> Дякуємо за
                  замовлення у Students Merch Shop!
                </div>
                <div className="receipt-footer-note">
                  Цей електронний товарний чек підтверджує здійснення безготівкової
                  оплати через платіжний сервіс Monobank Acquiring.
                </div>
              </div>
            </div>
          </>
        ) : null}
      </div>
    </div>
  );
};
