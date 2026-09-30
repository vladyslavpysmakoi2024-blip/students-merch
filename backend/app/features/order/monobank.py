import httpx

from app.core.config import FRONTEND_URL, MONOBANK_TOKEN, WEBHOOK_URL

MONO_API_URL = "https://api.monobank.ua/api/merchant/invoice/create"


async def create_invoice(amount: float, order_id: int) -> tuple[str | None, str | None]:
    headers = {"X-Token": MONOBANK_TOKEN}
    payload = {
        "amount": int(amount * 100),  # Монобанк приймає суму в копійках
        "ccy": 980,  # Код гривні
        "reference": str(order_id),
        "webHookUrl": WEBHOOK_URL,
        # Куди повернути клієнта після оплати
        "redirectUrl": f"{FRONTEND_URL.rstrip('/')}/me" if FRONTEND_URL else "http://localhost:3000/me",
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(MONO_API_URL, json=payload, headers=headers)
            if response.status_code == 200:
                data = response.json()
                # Повертаємо і урл, і інвойс
                return data.get("pageUrl"), data.get("invoiceId")
    except Exception as e:
        print(f"Monobank create_invoice error: {e}", flush=True)
    return None, None


async def get_invoice_status(invoice_id: str) -> dict | None:
    if not invoice_id or not MONOBANK_TOKEN:
        return None

    status_url = "https://api.monobank.ua/api/merchant/invoice/status"
    headers = {"X-Token": MONOBANK_TOKEN}
    params = {"invoiceId": invoice_id}

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(status_url, params=params, headers=headers)
            if response.status_code == 200:
                data = response.json()
                # Якщо є receiptId або дані квитанції, формуємо зручну відповідь
                receipt_id = data.get("receiptId")
                receipt_url = None
                if receipt_id:
                    receipt_url = f"https://check.gov.ua/check/{receipt_id}"
                elif data.get("pageUrl"):
                    receipt_url = data.get("pageUrl")

                return {
                    "invoice_id": invoice_id,
                    "status": data.get("status"),
                    "amount": data.get("amount", 0) / 100 if data.get("amount") else None,
                    "final_amount": data.get("finalAmount", 0) / 100 if data.get("finalAmount") else None,
                    "created_date": data.get("createdDate"),
                    "modified_date": data.get("modifiedDate"),
                    "receipt_id": receipt_id,
                    "receipt_url": receipt_url,
                    "raw": data,
                }
    except Exception as e:
        print(f"Monobank get_invoice_status error: {e}", flush=True)
    return None
