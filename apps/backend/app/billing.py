import os
import stripe
import httpx
import time
from typing import Dict, Any, Optional
from .utils import log_event
from .db.models import User

# Initialize Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")

# PayPal Config
PAYPAL_CLIENT_ID = os.getenv("PAYPAL_CLIENT_ID")
PAYPAL_CLIENT_SECRET = os.getenv("PAYPAL_CLIENT_SECRET")
PAYPAL_API_URL = "https://api-m.sandbox.paypal.com" if os.getenv("PAYPAL_MODE") != "live" else "https://api-m.paypal.com"

class BillingService:
    @staticmethod
    async def create_checkout_session(user_id: str, plan_id: str, ui_mode: str = 'hosted') -> Optional[Dict[str, Any]]:
        """
        Creates a Stripe Checkout Session for a given plan.
        ui_mode: 'hosted' (default redirect) or 'embedded' (for smart buttons)
        """
        try:
            user = await User.get(id=user_id)
            
            PRICE_MAP = {
                "PROFESSIONAL": os.getenv("STRIPE_PRICE_PROFESSIONAL", "price_prof_2900"),
                "SOVEREIGN": os.getenv("STRIPE_PRICE_SOVEREIGN", "price_sov_9900")
            }

            if plan_id not in PRICE_MAP:
                raise ValueError("Invalid Plan ID")

            session_params = {
                "automatic_payment_methods": {'enabled': True},
                "customer": user.stripe_customer_id,
                "client_reference_id": user_id,
                "line_items": [{
                    'price': PRICE_MAP[plan_id],
                    'quantity': 1,
                }],
                "mode": 'subscription',
                "metadata": {"plan": plan_id}
            }

            if ui_mode == 'embedded':
                session_params["ui_mode"] = 'embedded'
                session_params["return_url"] = os.getenv("FRONTEND_URL", "http://localhost:8080") + "/settings?session_id={CHECKOUT_SESSION_ID}"
            else:
                session_params["success_url"] = os.getenv("FRONTEND_URL", "http://localhost:8080") + "/settings?success=true"
                session_params["cancel_url"] = os.getenv("FRONTEND_URL", "http://localhost:8080") + "/settings?canceled=true"

            session = stripe.checkout.Session.create(**session_params)
            
            log_event("BILLING", f"Created Stripe session ({ui_mode}) for user: {user_id} | Plan: {plan_id}")
            
            return {
                "url": session.get("url"),
                "clientSecret": session.get("client_secret"),
                "id": session.id
            }
        except Exception as e:
            log_event("ERROR", f"Stripe Session Creation Failed: {e}")
            return None

    @staticmethod
    async def handle_webhook(payload: bytes, sig_header: str) -> Dict[str, Any]:
        """
        Processes Stripe Webhooks to update user plans.
        """
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, WEBHOOK_SECRET
            )
        except ValueError as e:
            return {"status": "error", "msg": "Invalid payload"}
        except stripe.error.SignatureVerificationError as e:
            return {"status": "error", "msg": "Invalid signature"}

        # Handle successful payment/subscription
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            user_id = session.get('client_reference_id')
            plan = session.get('metadata', {}).get('plan', 'COMMUNITY')
            customer_id = session.get('customer')

            if user_id:
                user = await User.get(id=user_id)
                user.plan = plan
                if not user.stripe_customer_id:
                    user.stripe_customer_id = customer_id
                await user.save()
                log_event("BILLING", f"User {user_id} upgraded to {plan}")

        return {"status": "success"}

    @staticmethod
    async def get_portal_url(user_id: str) -> Optional[str]:
        """
        Returns the Stripe Customer Portal URL for subscription management.
        """
        try:
            user = await User.get(id=user_id)
            if not user.stripe_customer_id:
                return None
            
            session = stripe.billing_portal.Session.create(
                customer=user.stripe_customer_id,
                return_url=os.getenv("FRONTEND_URL", "http://localhost:8080") + "/settings"
            )
            return session.url
        except Exception as e:
            log_event("ERROR", f"Stripe Portal Creation Failed: {e}")
            return None

class PayPalService:
    @staticmethod
    async def get_access_token() -> Optional[str]:
        """Fetches auth token from PayPal API."""
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    f"{PAYPAL_API_URL}/v1/oauth2/token",
                    auth=(PAYPAL_CLIENT_ID, PAYPAL_CLIENT_SECRET),
                    data={"grant_type": "client_credentials"}
                )
                return resp.json().get("access_token")
        except Exception as e:
            log_event("ERROR", f"PayPal Auth Failed: {e}")
            return None

    @staticmethod
    async def create_order(user_id: str, plan_id: str) -> Optional[Dict[str, Any]]:
        """Creates a PayPal order for the specified plan."""
        token = await PayPalService.get_access_token()
        if not token: return None

        pricing = {"PROFESSIONAL": "29.00", "SOVEREIGN": "99.00"}
        amount = pricing.get(plan_id)
        if not amount: return None

        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    f"{PAYPAL_API_URL}/v2/checkout/orders",
                    headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                    json={
                        "intent": "CAPTURE",
                        "purchase_units": [{
                            "reference_id": user_id,
                            "amount": {"currency_code": "USD", "value": amount},
                            "description": f"Sanctum Brain - {plan_id} Subscription"
                        }],
                        "application_context": {
                            "brand_name": "Sanctum Brain",
                            "user_action": "PAY_NOW"
                        }
                    }
                )
                return resp.json()
        except Exception as e:
            log_event("ERROR", f"PayPal Order Creation Failed: {e}")
            return None

    @staticmethod
    async def capture_order(order_id: str) -> Dict[str, Any]:
        """Captures a PayPal order and updates the user's plan."""
        token = await PayPalService.get_access_token()
        if not token: return {"status": "error", "msg": "Auth failed"}

        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    f"{PAYPAL_API_URL}/v2/checkout/orders/{order_id}/capture",
                    headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
                )
                data = resp.json()
                
                if data.get("status") == "COMPLETED":
                    purchase_unit = data["purchase_units"][0]
                    user_id = purchase_unit.get("reference_id")
                    
                    # Logic to determine plan from amount
                    amount = purchase_unit["payments"]["captures"][0]["amount"]["value"]
                    plan = "PROFESSIONAL" if amount == "29.00" else "SOVEREIGN"
                    
                    if user_id:
                        user = await User.get(id=user_id)
                        user.plan = plan
                        await user.save()
                        log_event("BILLING", f"PayPal Upgrade: User {user_id} to {plan}")
                        return {"status": "success", "plan": plan}
                
                return {"status": "error", "msg": "Capture failed"}
        except Exception as e:
            log_event("ERROR", f"PayPal Capture Failed: {e}")
            return {"status": "error", "msg": str(e)}

    @staticmethod
    async def handle_webhook(payload: Dict[str, Any]) -> Dict[str, Any]:
        """Processes PayPal Webhooks for subscription events."""
        event_type = payload.get("event_type")
        resource = payload.get("resource", {})
        
        # Subscription Created/Activated
        if event_type in ["BILLING.SUBSCRIPTION.CREATED", "BILLING.SUBSCRIPTION.ACTIVATED"]:
            sub_id = resource.get("id")
            custom_id = resource.get("custom_id") # We pass user_id here
            
            if custom_id:
                user = await User.get_or_none(id=custom_id)
                if user:
                    user.paypal_subscription_id = sub_id
                    # Extract plan from PayPal Plan ID if possible, or wait for sale event
                    await user.save()
                    log_event("BILLING", f"PayPal Subscription {event_type}: User {custom_id}")

        # Payment Succeeded
        elif event_type == "PAYMENT.SALE.COMPLETED":
            sub_id = resource.get("billing_agreement_id")
            if sub_id:
                user = await User.get_or_none(paypal_subscription_id=sub_id)
                if user:
                    # Upgrade plan based on amount if not already set
                    amount = resource.get("amount", {}).get("total")
                    plan = "PROFESSIONAL" if amount == "29.00" else "SOVEREIGN"
                    user.plan = plan
                    await user.save()
                    log_event("BILLING", f"PayPal Payment Success: User {user.id} - Plan {plan}")

        # Subscription Cancelled/Expired
        elif event_type in ["BILLING.SUBSCRIPTION.CANCELLED", "BILLING.SUBSCRIPTION.EXPIRED"]:
            sub_id = resource.get("id")
            user = await User.get_or_none(paypal_subscription_id=sub_id)
            if user:
                user.plan = "COMMUNITY"
                user.paypal_subscription_id = None
                await user.save()
                log_event("BILLING", f"PayPal Subscription Cancelled: User {user.id}")

        return {"status": "success"}

class PayPalSubscriptionService:
    @staticmethod
    async def create_subscription(user_id: str, plan_id: str) -> Optional[Dict[str, Any]]:
        """
        Creates a PayPal subscription for the specified plan with a 7-day trial.
        Note: Free trial logic is usually defined in the PayPal Plan itself.
        If the plan doesn't have a trial, we can't easily override it here via V1/Subscriptions.
        We assume the PLAN_IDs in PayPal are configured with a 7-day trial.
        """
        token = await PayPalService.get_access_token()
        if not token: return None

        PLAN_MAP = {
            "PROFESSIONAL": os.getenv("PAYPAL_PLAN_ID_PROFESSIONAL"),
            "SOVEREIGN": os.getenv("PAYPAL_PLAN_ID_SOVEREIGN")
        }
        paypal_plan_id = PLAN_MAP.get(plan_id)
        if not paypal_plan_id: return None

        try:
            user = await User.get(id=user_id)
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    f"{PAYPAL_API_URL}/v1/billing/subscriptions",
                    headers={
                        "Authorization": f"Bearer {token}",
                        "Content-Type": "application/json",
                        "Accept": "application/json",
                        "PayPal-Request-Id": f"sub_{user_id}_{int(time.time())}"
                    },
                    json={
                        "plan_id": paypal_plan_id,
                        "custom_id": user_id,
                        "subscriber": {
                            "name": {"given_name": user.name.split()[0] if user.name else "User"},
                            "email_address": user.email
                        },
                        "application_context": {
                            "brand_name": "Sanctum Brain",
                            "user_action": "SUBSCRIBE_NOW",
                            "return_url": os.getenv("FRONTEND_URL", "http://localhost:8080") + "/settings?success=true",
                            "cancel_url": os.getenv("FRONTEND_URL", "http://localhost:8080") + "/settings?canceled=true"
                        }
                    }
                )
                return resp.json()
        except Exception as e:
            log_event("ERROR", f"PayPal Subscription Creation Failed: {e}")
            return None

    @staticmethod
    async def cancel_subscription(user_id: str, reason: str = "User requested cancellation") -> bool:
        """Cancels an active PayPal subscription."""
        user = await User.get_or_none(id=user_id)
        if not user or not user.paypal_subscription_id:
            return False

        token = await PayPalService.get_access_token()
        if not token: return False

        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    f"{PAYPAL_API_URL}/v1/billing/subscriptions/{user.paypal_subscription_id}/cancel",
                    headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                    json={"reason": reason}
                )
                if resp.status_code == 204:
                    user.plan = "COMMUNITY"
                    user.paypal_subscription_id = None
                    await user.save()
                    return True
                return False
        except Exception as e:
            log_event("ERROR", f"PayPal Subscription Cancellation Failed: {e}")
            return False

    @staticmethod
    async def upgrade_subscription(user_id: str, new_plan_id: str) -> Optional[Dict[str, Any]]:
        """
        Upgrades an existing subscription to a higher level.
        In PayPal, this typically involves 'revising' the subscription.
        """
        user = await User.get_or_none(id=user_id)
        if not user or not user.paypal_subscription_id:
            return await PayPalSubscriptionService.create_subscription(user_id, new_plan_id)

        token = await PayPalService.get_access_token()
        if not token: return None

        PLAN_MAP = {
            "PROFESSIONAL": os.getenv("PAYPAL_PLAN_ID_PROFESSIONAL"),
            "SOVEREIGN": os.getenv("PAYPAL_PLAN_ID_SOVEREIGN")
        }
        new_paypal_plan_id = PLAN_MAP.get(new_plan_id)
        
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    f"{PAYPAL_API_URL}/v1/billing/subscriptions/{user.paypal_subscription_id}/revise",
                    headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                    json={"plan_id": new_paypal_plan_id}
                )
                return resp.json()
        except Exception as e:
            log_event("ERROR", f"PayPal Subscription Upgrade Failed: {e}")
            return None
