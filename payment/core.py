import decimal
import hashlib
from urllib import parse
from urllib.parse import urlparse, quote
import json

from config import MERCHANT_LOGIN, PASSWORD1, PASSWORD2, SUBSCRIPTION_PRICE


def calculate_signature(*args) -> str:
    """
    Create signature MD5.
    """
    return hashlib.md5(':'.join(str(arg) for arg in args).encode()).hexdigest()

def check_signature_result(
    order_number: int,  # invoice number
    received_sum: decimal,  # cost of goods, RU
    received_signature: hex,  # SignatureValue
    password: str  # Merchant password
) -> bool:
    signature = calculate_signature(received_sum, order_number, password)
    if signature.lower() == received_signature.lower():
        return True
    return False

def generate_link(payment_id: int, description: str):
    """
    URL for redirection of the customer to the service.
    """
    reciept = {
        "sno": "usn_income_outcome",
        "items": [
            {
                "name": "Подписка на информационный канал",
                "quantity": 1,
                "sum": SUBSCRIPTION_PRICE,
                "payment_method": "full_payment",
                "payment_object": "service",
                "tax": "none"
            }
        ]
    }
    # Преобразуем JSON в строку
    json_string = json.dumps(reciept, ensure_ascii=False)

    # URL-кодируем строку
    encoded_json = quote(json_string)
    #print(encoded_json)
    signature = calculate_signature(
        MERCHANT_LOGIN,
        SUBSCRIPTION_PRICE,
        payment_id,
        encoded_json,
        PASSWORD1
        #password_2
    )
    robokassa_payment_url = "https://auth.robokassa.ru/Merchant/Index.aspx"
    data = {
        'MerchantLogin': MERCHANT_LOGIN,
        'OutSum': SUBSCRIPTION_PRICE,
        'InvoiceID': payment_id,
        'Description': description,
        'SignatureValue': signature,
        'Receipt': encoded_json
    }
    return f'{robokassa_payment_url}?{parse.urlencode(data)}'

