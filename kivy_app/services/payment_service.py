"""
Payment service for Kivy app.

Card entry in a bare Kivy app can't use Stripe.js/Elements or a mobile SDK,
and Stripe restricts raw card-number APIs to approved integrations for PCI
reasons. So checkout here uses Stripe's test-mode card tokens (tok_visa,
etc.) - these are pre-made tokens that stand in for a real card and are
safe to exchange for a PaymentMethod using only the publishable key, in
test mode. This gives a real, working Stripe payment flow end-to-end
without needing raw card fields or a webview.
"""
import requests
from typing import Tuple
from kivy_app.services.api_client import api_client
from kivy_app.config import STRIPE_PUBLISHABLE_KEY

STRIPE_API_BASE = "https://api.stripe.com/v1"

# label -> Stripe test token (https://stripe.com/docs/testing#cards)
TEST_CARDS = [
    ("Visa - succeeds", "tok_visa"),
    ("Visa (debit) - succeeds", "tok_visa_debit"),
    ("Mastercard - succeeds", "tok_mastercard"),
    ("Test card - declined", "tok_chargeDeclined"),
]


def create_payment_intent(order_id: str) -> dict:
    """Create a Stripe payment intent for an order via the backend."""
    return api_client.post(
        "/api/v1/payments/create-payment-intent", params={"order_id": order_id}
    )


def confirm_payment_backend(order_id: str, payment_intent_id: str) -> dict:
    """Tell the backend the payment succeeded so it can finalize the order and clear the cart."""
    return api_client.post(
        "/api/v1/payments/confirm-payment",
        params={"order_id": order_id, "payment_intent_id": payment_intent_id},
    )


def _create_payment_method_from_token(card_token: str) -> str:
    """Create a Stripe PaymentMethod from a test card token using the publishable key."""
    response = requests.post(
        f"{STRIPE_API_BASE}/payment_methods",
        auth=(STRIPE_PUBLISHABLE_KEY, ""),
        data={"type": "card", "card[token]": card_token},
    )
    response.raise_for_status()
    return response.json()["id"]


def _confirm_payment_intent(payment_intent_id: str, payment_method_id: str) -> dict:
    """Confirm a Stripe PaymentIntent client-side using the publishable key."""
    response = requests.post(
        f"{STRIPE_API_BASE}/payment_intents/{payment_intent_id}/confirm",
        auth=(STRIPE_PUBLISHABLE_KEY, ""),
        data={"payment_method": payment_method_id},
    )
    response.raise_for_status()
    return response.json()


def pay_for_order(order_id: str, card_token: str) -> Tuple[bool, str]:
    """
    Run the full payment flow for an order: create a PaymentIntent, confirm
    it with a test card token, and notify the backend once it succeeds.

    Args:
        order_id: Order UUID to pay for
        card_token: One of the Stripe test tokens from TEST_CARDS

    Returns:
        (succeeded, status) - status is Stripe's PaymentIntent status
        (e.g. "succeeded", "requires_payment_method" on a declined card)
    """
    intent_data = create_payment_intent(order_id)
    payment_intent_id = intent_data["payment_intent_id"]

    payment_method_id = _create_payment_method_from_token(card_token)
    confirmed = _confirm_payment_intent(payment_intent_id, payment_method_id)

    status = confirmed.get("status", "unknown")
    if status == "succeeded":
        confirm_payment_backend(order_id, payment_intent_id)
        return True, status

    return False, status
