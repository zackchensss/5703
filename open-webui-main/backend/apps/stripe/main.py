from fastapi import FastAPI, Request, HTTPException, APIRouter
import stripe
import threading
import time
from fastapi.responses import RedirectResponse
from apps.webui.models.users import Users

stripe.api_key = 'sk_test_51PpnBARwKnsYpxFvqOIE6TwPUD4MPyHODJVOcnlsqrJbD8U82aN98ZUwu5NmtXAHuMyQKjPORI089WcNT9d4du6300KTgiURES'
webhook_secret = 'whsec_45695097e5d997dbbb477f49b5f9224400d1b5764b9eb0acbd85e3a310a1a0be'

router = APIRouter()

@router.post("/api/webhook/stripe")
async def stripe_webhook(request: Request):
    global customer_email, price, price_id, product, product_id, status

    payload = await request.body()
    sig_header = request.headers.get('Stripe-Signature')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        raise HTTPException(status_code=400, detail="Invalid signature")

    event_type = event['type']
    data = event['data']['object']

    customer_email = data.get('customer_email')
    if not customer_email:
        customer_id = data.get('customer')
        if customer_id:
            customer = stripe.Customer.retrieve(customer_id)
            customer_email = customer.email

    if event_type == 'checkout.session.completed':
        status = data['payment_status']
        await save_to_database()

    return {"status": "success"}

async def save_to_database():
    global customer_email, price, price_id, product, product_id, status
    print
    try:
        user = Users.get_user_by_email(customer_email)
        if user:
            user.subscription_status = status
            if product == "open webui ultra":
                user.subscription_expiration = int(time.time()) + 365 * 24 * 60 * 60  # yearly
            elif product == "open webui pro":
                user.subscription_expiration = int(time.time()) + 30 * 24 * 60 * 60  # monthly

            await Users.update_user_by_id(user.id, {
                "subscription_status": user.subscription_status,
                "subscription_expiration": user.subscription_expiration,
            })
    except Exception as e:
        print(f"Wrong when saving the info: {e}")

@router.get("/subscribe")
async def subscribe():
    #mini
    stripe_checkout_url = "https://buy.stripe.com/test_9AQfZ31oIbhL3Ic28a"

    #pro
    #stripe_checkout_url = "https://buy.stripe.com/test_5kA149c3m3PjceI3cc"

    #ultra
    #stripe_checkout_url = "https://buy.stripe.com/test_eVa5kpebudpT3Ic6op"
    return RedirectResponse(url=stripe_checkout_url)

# cancel
@router.post("/cancel-subscription")
async def cancel_subscription(request: Request):
    try:
        form_data = await request.json()
        subscription_id = form_data['subscription_id']
        subscription = stripe.Subscription.cancel(subscription_id, at_period_end=True)
        return subscription
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
