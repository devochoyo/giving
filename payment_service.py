import os
import uuid

import requests

from extension import db
from model import Payment

FLW_URL = "https://api.flutterwave.com/v3"


def get_headers():
    f_secret_key = os.getenv("F_SECRET_KEY")
    return {
        "Authorization": "Bearer " + str(f_secret_key),
        "Content-Type": "application/json",
    }


def start_payment(name, email, currency, amount, redirect_url):
    """Create the payment on Flutterwave and return the checkout link."""
    reference = str(uuid.uuid4())

    data = {
        "tx_ref": reference,
        "amount": amount,
        "currency": currency,
        "redirect_url": redirect_url,
        "customer": {"email": email, "name": name},
        "customizations": {"title": "Support"},
    }

    try:
        response = requests.post(
            FLW_URL + "/payments", json=data, headers=get_headers(), timeout=30
        )
        result = response.json()
    except Exception:
        return None

    if result.get("status") != "success":
        return None

    # save the payment as pending
    payment = Payment(
        reference=reference,
        name=name,
        email=email,
        currency=currency,
        amount=amount,
        status="pending",
    )
    db.session.add(payment)
    db.session.commit()

    return result["data"]["link"]


def verify_payment(reference, transaction_id):
    """Ask Flutterwave if the payment really went through. Returns True or False."""
    payment = Payment.query.filter_by(reference=reference).first()
    if payment is None:
        print("verify: no payment found for reference", reference)
        return False

    # already confirmed before (user refreshed the page)
    if payment.status == "paid":
        return True

    if transaction_id:
        url = FLW_URL + "/transactions/" + str(transaction_id) + "/verify"
    else:
        url = FLW_URL + "/transactions/verify_by_reference?tx_ref=" + reference

    try:
        response = requests.get(url, headers=get_headers(), timeout=30)
        result = response.json()
    except Exception as error:
        print("verify: request to Flutterwave failed:", error)
        return False

    data = result.get("data") or {}

    paid = (
        data.get("status") == "successful"
        and data.get("tx_ref") == reference
        and str(data.get("currency", "")).upper() == payment.currency
        and float(data.get("amount", 0)) >= payment.amount - 0.01
    )

    if not paid:
        print("verify: not accepted, Flutterwave answered:", result)

    payment.status = "paid" if paid else "failed"
    db.session.commit()

    return paid


def mark_failed(reference):
    payment = Payment.query.filter_by(reference=reference).first()
    if payment is not None and payment.status == "pending":
        payment.status = "failed"
        db.session.commit()
