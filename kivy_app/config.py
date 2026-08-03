"""
Client-side configuration for the Kivy app.

These are safe to ship in a client build: the API base URL is just where
the backend lives, and the Stripe key here must be the *publishable* key
(pk_...), never the secret key. Override via environment variables for
different environments (e.g. staging vs. local).
"""
import os

API_BASE_URL = os.environ.get("FOODAPP_API_BASE_URL", "http://localhost:8000")

# Must match the STRIPE_PUBLISHABLE_KEY configured on the backend (.env).
STRIPE_PUBLISHABLE_KEY = os.environ.get(
    "STRIPE_PUBLISHABLE_KEY", "pk_test_your_stripe_publishable_key"
)
