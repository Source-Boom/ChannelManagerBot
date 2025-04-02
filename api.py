from flask import Flask, request, abort
import hashlib
import traceback
import requests
import logging
import sys

app = Flask(__name__)

# Данные от Robokassa (замени на свои)
from config import PASSWORD2, PASSWORD1, TOKEN, INVITATION_LINK, SUBSCRIPTION_PRICE
from payment.core import check_signature_result
from db.crud import db

logging.basicConfig(filename=f"/root/manager_bot/server.logs", level=logging.ERROR)
sys.stdout = open(f"/root/manager_bot/server.prints", "wt")

SEND_MESSAGE_URL = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

def generate_signature(*args):
    """Генерация контрольной подписи MD5"""
    signature_str = ":".join(str(arg) for arg in args)
    return hashlib.md5(signature_str.encode()).hexdigest()

@app.route("/robokassa/result", methods=["POST", "GET"])
def robokassa_result():
    """Обработчик Result URL"""
    try:
        cost = request.args.get('OutSum')
        number = request.args.get('InvId')
        signature = request.args.get('SignatureValue')


        if check_signature_result(number, cost, signature, PASSWORD2):
            print("YES_PAY")
            user_id = db.select_payment(pay_id=int(number))
            if user_id == None:
                return "no_such_order"
            if not db.is_user_sync(user_id):
                db.add_user_sync(user_id)
            
            db.replenish_user_balance_sync(user_id)
            if not db.is_user_subscription_active_sync(user_id):
                db.update_subscription_sync(user_id)
                try:
                    reply_markup = {
                        "inline_keyboard": [
                            [{"text": "Перейти в канал", "url": INVITATION_LINK}]
                        ]
                    }
                    params = {
                        "chat_id": user_id,
                        "text": 'Оплата прошла успешно!\n\nДоступ в канал Style by Inna открыт!\n\nПодайте заявку на вступление в него по ссылке ниже. Бот автоматически её одобрит!',
                        "reply_markup": reply_markup
                    }
                    response = requests.post(SEND_MESSAGE_URL, json=params)
                except:
                    print('An error occurred')
            else:
                params = {
                    "chat_id": user_id,
                    "text": f"Оплата прошла успешно!\n\n{SUBSCRIPTION_PRICE}₽ уже зачислены на ваш счёт!\nПри истечении срока текущей подписки {SUBSCRIPTION_PRICE}₽ будут автоматически списаны со счёта"
                }
                response = requests.post(SEND_MESSAGE_URL, json=params)
            print("YES_END")
            return f'OK{number}'
        print("NO_END")
        return "bad sign"
    except Exception as e:
        traceback.print_exc()
        print("Ошибка обработки Result URL:", e)
        abort(500)

@app.route("/robokassa/succes", methods=["GET"])
def robokassa_success():
    cost = request.args.get('OutSum')
    number = request.args.get('InvId')
    signature = request.args.get('SignatureValue')
    print("SUCCES")
    if check_signature_result(number, cost, signature, PASSWORD1):
        print("YEEES")
        return("Оплата прошла успешно")
    else:
        abort(500)

@app.route("/robokassa/fail", methods=["GET"])
def robokassa_fail():
    return("Ошибка оплаты!")


if __name__ == "__main__":
    app.run()