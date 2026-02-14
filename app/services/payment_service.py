"""
Payment service for Stripe integration.
"""
import stripe
from typing import Optional
from decimal import Decimal
from app.config import settings

# Initialize Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


def create_payment_intent(amount: Decimal, currency: str = "usd") -> dict:
    """
    Create a Stripe payment intent.
    
    Args:
        amount: Amount to charge (in dollars)
        currency: Currency code
    
    Returns:
        Payment intent data including client_secret
    """
    try:
        # Convert to cents for Stripe
        amount_cents = int(amount * 100)
        
        intent = stripe.PaymentIntent.create(
            amount=amount_cents,
            currency=currency,
            automatic_payment_methods={
                "enabled": True,
            },
        )
        
        return {
            "client_secret": intent.client_secret,
            "payment_intent_id": intent.id,
            "amount": amount,
            "currency": currency
        }
    except stripe.error.StripeError as e:
        raise Exception(f"Stripe error: {str(e)}")


def confirm_payment(payment_intent_id: str) -> bool:
    """
    Confirm a payment intent status.
    
    Args:
        payment_intent_id: Stripe payment intent ID
    
    Returns:
        True if payment succeeded, False otherwise
    """
    try:
        intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        return intent.status == "succeeded"
    except stripe.error.StripeError:
        return False


def create_checkout_session(
    order_id: str,
    amount: Decimal,
    success_url: str,
    cancel_url: str
) -> dict:
    """
    Create a Stripe checkout session.
    
    Args:
        order_id: Order UUID
        amount: Amount to charge
        success_url: URL to redirect on success
        cancel_url: URL to redirect on cancel
    
    Returns:
        Checkout session data
    """
    try:
        amount_cents = int(amount * 100)
        
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "product_data": {
                            "name": "Food Order",
                            "description": f"Order #{order_id}",
                        },
                        "unit_amount": amount_cents,
                    },
                    "quantity": 1,
                },
            ],
            mode="payment",
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={
                "order_id": order_id
            }
        )
        
        return {
            "session_id": session.id,
            "url": session.url
        }
    except stripe.error.StripeError as e:
        raise Exception(f"Stripe error: {str(e)}")


def handle_webhook_event(payload: bytes, sig_header: str) -> Optional[dict]:
    """
    Handle Stripe webhook event.
    
    Args:
        payload: Raw request body
        sig_header: Stripe signature header
    
    Returns:
        Event data or None if verification fails
    """
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
        return event
    except (ValueError, stripe.error.SignatureVerificationError):
        return None
