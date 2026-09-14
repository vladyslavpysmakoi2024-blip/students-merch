import httpx

from app.core.config import MONOBANK_TOKEN, WEBHOOK_URL

MONO_API_URL = "https://api.monobank.ua/api/merchant/invoice/create"


async def create_invoice(amount: float, order_id: int) -> str | None:
    headers = {"X-Token": MONOBANK_TOKEN}
    payload = {
        "amount": int(amount * 100),  # Монобанк приймає суму в копійках
        "ccy": 980,  # Код гривні
        "reference": str(order_id),
        "webHookUrl": WEBHOOK_URL,
        "redirectUrl": "http://localhost:3000/me",  # Куди повернути клієнта після оплати
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(MONO_API_URL, json=payload, headers=headers)
        if response.status_code == 200:
            data = response.json()
            # Повертаємо і урл, і інвойс
            return data.get("pageUrl"), data.get("invoiceId")
        return None, None
