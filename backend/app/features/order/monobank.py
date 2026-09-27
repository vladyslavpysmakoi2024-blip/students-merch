import base64
import binascii
from decimal import Decimal

import httpx
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec

from app.core.config import FRONTEND_URL, MONOBANK_TOKEN, WEBHOOK_URL

MONO_API_URL = "https://api.monobank.ua/api/merchant/invoice/create"
MONO_PUBKEY_URL = "https://api.monobank.ua/api/merchant/pubkey"


async def create_invoice(amount: Decimal, order_id: int) -> str | None:
    headers = {"X-Token": MONOBANK_TOKEN}
    payload = {
        "amount": int(amount * 100),  # Монобанк приймає суму в копійках
        "ccy": 980,  # Код гривні
        "reference": str(order_id),
        "webHookUrl": WEBHOOK_URL,
        # Куди повернути клієнта після оплати
        "redirectUrl": f"{FRONTEND_URL}/me",
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(MONO_API_URL, json=payload, headers=headers)
        if response.status_code == 200:
            data = response.json()
            # Повертаємо і урл, і інвойс
            return data.get("pageUrl"), data.get("invoiceId")
        return None, None


async def is_valid_webhook_signature(body: bytes, x_sign: str) -> bool:
    async with httpx.AsyncClient() as client:
        response = await client.get(MONO_PUBKEY_URL, headers={"X-Token": MONOBANK_TOKEN})
        response.raise_for_status()

    public_key = serialization.load_pem_public_key(base64.b64decode(response.json()["key"]))

    try:
        public_key.verify(base64.b64decode(x_sign), body, ec.ECDSA(hashes.SHA256()))
    except (InvalidSignature, binascii.Error):
        return False
    return True
