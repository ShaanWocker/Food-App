"""
Payment routes for Stripe integration.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.order import PaymentStatus
from app.services.payment_service import (
    create_payment_intent,
    create_checkout_session,
    handle_webhook_event
)
from app.services.order_service import (
    get_order_by_id,
    update_payment_status
)
from app.services.cart_service import clear_cart

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.post("/create-payment-intent")
async def create_payment(
    order_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a Stripe payment intent for an order.
    
    Args:
        order_id: Order UUID
        current_user: Current authenticated user
        db: Database session
    
    Returns:
        Payment intent data with client_secret
    
    Raises:
        HTTPException: If order not found or already paid
    """
    order = get_order_by_id(db, order_id, str(current_user.id))
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    if order.payment_status == PaymentStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order already paid"
        )
    
    try:
        payment_data = create_payment_intent(order.total_price)
        return payment_data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/create-checkout-session")
async def create_checkout(
    order_id: str,
    success_url: str,
    cancel_url: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a Stripe checkout session for an order.
    
    Args:
        order_id: Order UUID
        success_url: URL to redirect on success
        cancel_url: URL to redirect on cancel
        current_user: Current authenticated user
        db: Database session
    
    Returns:
        Checkout session data
    
    Raises:
        HTTPException: If order not found or already paid
    """
    order = get_order_by_id(db, order_id, str(current_user.id))
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    if order.payment_status == PaymentStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order already paid"
        )
    
    try:
        checkout_data = create_checkout_session(
            order_id,
            order.total_price,
            success_url,
            cancel_url
        )
        return checkout_data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/confirm-payment")
async def confirm_payment(
    order_id: str,
    payment_intent_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Confirm payment and update order status.
    
    Args:
        order_id: Order UUID
        payment_intent_id: Stripe payment intent ID
        current_user: Current authenticated user
        db: Database session
    
    Returns:
        Success message
    
    Raises:
        HTTPException: If order not found
    """
    order = get_order_by_id(db, order_id, str(current_user.id))
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Update order payment status
    update_payment_status(
        db,
        order_id,
        PaymentStatus.COMPLETED,
        payment_intent_id
    )
    
    # Clear user's cart after successful payment
    clear_cart(db, str(current_user.id))
    
    return {"message": "Payment confirmed successfully"}


@router.post("/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Handle Stripe webhook events.
    
    Args:
        request: Raw request with Stripe signature
        db: Database session
    
    Returns:
        Success message
    """
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    
    event = handle_webhook_event(payload, sig_header)
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid signature"
        )
    
    # Handle the event
    if event["type"] == "payment_intent.succeeded":
        payment_intent = event["data"]["object"]
        # Update order status based on payment_intent metadata
        # This would need order_id from metadata
        pass
    
    return {"status": "success"}
