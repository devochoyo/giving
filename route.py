from flask import Blueprint, redirect, render_template, request, url_for

from payment_service import mark_failed, start_payment, verify_payment

home_bp = Blueprint("home", __name__)
payment_bp = Blueprint("payment", __name__)
success_bp = Blueprint("success", __name__)
error_bp = Blueprint("error", __name__)

CURRENCIES = ["USD", "ZAR", "NGN", "GBP", "EUR", "GHS", "KES"]


@home_bp.route("/")
def home():
    return render_template("home.html", currencies=CURRENCIES)


@home_bp.route("/health")
def health():
    return "OK. API is active.", 200


@payment_bp.route("/pay", methods=["POST"])
def pay():
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    currency = request.form.get("currency", "").strip().upper()
    amount = request.form.get("amount", "").strip()

    try:
        amount = float(amount)
    except ValueError:
        return redirect(url_for("error.failed"))

    if not name or not email or currency not in CURRENCIES or amount <= 0:
        return redirect(url_for("error.failed"))

    redirect_url = url_for("payment.callback", _external=True)
    link = start_payment(name, email, currency, amount, redirect_url)

    if link is None:
        return redirect(url_for("error.failed"))

    return redirect(link)


@payment_bp.route("/callback")
def callback():
    # Flutterwave sends the user back here after payment
    status = request.args.get("status")
    reference = request.args.get("tx_ref")
    transaction_id = request.args.get("transaction_id")

    if not reference:
        return redirect(url_for("error.failed"))

    if status == "cancelled":
        mark_failed(reference)
        return redirect(url_for("error.failed"))

    # we do not trust the url, Flutterwave decides if it was paid
    if verify_payment(reference, transaction_id):
        return redirect(url_for("success.success"))

    return redirect(url_for("error.failed"))


@success_bp.route("/success")
def success():
    return render_template("success.html")


@error_bp.route("/failed")
def failed():
    return render_template("failed.html")
