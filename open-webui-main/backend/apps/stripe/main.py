from fastapi import FastAPI, Request, HTTPException, APIRouter
import stripe
import threading
import time
from fastapi.responses import RedirectResponse
from apps.webui.models.users import Users
from flask import Flask, redirect, jsonify, request
import logging


stripe.api_key = 'sk_test_51PpnBARwKnsYpxFvqOIE6TwPUD4MPyHODJVOcnlsqrJbD8U82aN98ZUwu5NmtXAHuMyQKjPORI089WcNT9d4du6300KTgiURES'
webhook_secret = 'whsec_45695097e5d997dbbb477f49b5f9224400d1b5764b9eb0acbd85e3a310a1a0be'

##router = APIRouter()
app = FastAPI()

customer_email = None
price = None
price_id = None
product = None
product_id = None
status = None
log = logging.getLogger(__name__)


@app.post('/stripe')
async def stripe_webhook(request: Request):
    global customer_email, price, price_id, product, product_id, status
    log.warning("Received Stripe webhook")
    payload = await request.body()
    sig_header = request.headers.get('Stripe-Signature')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
    except ValueError as e:
        return {"error": "Invalid payload"}, 400
    except stripe.error.SignatureVerificationError as e:
        return {"error": "Invalid signature"}, 400

    event_type = event['type']
    data = event['data']['object']
    log.warning(f"Event type: {event_type}")
    log.warning(f"Event data: {data}")
    customer_email = data.get('customer_email')
    if not customer_email:
        customer_id = data.get('customer')
        if customer_id:
            customer = stripe.Customer.retrieve(customer_id)
            customer_email = customer.email

    if event_type in ['customer.subscription.created', 'customer.subscription.updated']:
        if 'items' in data:
            price_id = data['items']['data'][0]['price']['id']
            product_id = data['items']['data'][0]['price']['product']

            if price_id == "price_1PsP8yRwKnsYpxFv5d2FxFUI":
                price = "99.99"
            elif price_id == "price_1PrbewRwKnsYpxFvTZXXC1JK":
                price = "9.99"
            elif price_id == "price_1PuQKORwKnsYpxFvKj70Ftv3":
                price = "4.99"
            else:
                price = "error"

            if product_id == "prod_QjsurwseJK95jp":
                product = "open webui ultra"
            elif product_id == "prod_Qj3merrWlM46hw":
                product = "open webui pro"
            elif product_id == "prod_QlyGyQkYhUTekg":
                product = "open webui mini"
            else:
                product = "error"
        else:
            print("No items found in the subscription data.")

    if event_type == 'checkout.session.completed':
        status = data['payment_status']
        await save_to_database()
        logging.warning(f"checkout session completed")
        print("checkout.session.completed")
        # add more success logic

    elif event_type == 'customer.subscription.deleted':
        print(f"Subscription {data['id']} deleted")
        # add delete logic

    elif event_type == 'invoice.payment_succeeded':
        print("'invoice.payment_succeeded'")

    elif event_type == 'payment_method.attached':
        print("payment_method.attached")

    else:
        print(f"Unhandled event type: {event_type}")

    return {"status": "success"}, 200

async def save_to_database():
    global customer_email, price, product, status
    print(f"Saving to database: {customer_email}, {price}, {product}, {status}")

    try:
        user = Users.get_user_by_email(customer_email)
        if user:
            expiration = 0
            if product == "open webui ultra":
                expiration = int(time.time()) + 365 * 24 * 60 * 60  # yearly
            elif product == "open webui pro":
                expiration = int(time.time()) + 30 * 24 * 60 * 60  # monthly
            elif product == "open webui mini":
                expiration = int(time.time()) + 7 * 24 * 60 * 60  # weekly

            updated_user = Users.update_user_by_id(user.id, {
                "subscription_status": status,
                "subscription_expiration": expiration,
            })

            if updated_user:
                print(f"Successfully updated subscription for user: {updated_user.email}")
            else:
                print(f"Failed to update subscription for user: {user.email}")
        else:
            print(f"No user found with email: {customer_email}")
    except Exception as e:
        print(f"Error when saving the subscription info: {e}")

@app.get("/subscribe")
async def subscribe():
    log.warning("Received Stripe subscribe request")
    ### mini
    stripe_checkout_url = "https://buy.stripe.com/test_9AQfZ31oIbhL3Ic28a"
    ### pro
    # stripe_checkout_url = "https://buy.stripe.com/test_5kA149c3m3PjceI3cc"
    ### ultra
    # stripe_checkout_url = "https://buy.stripe.com/test_eVa5kpebudpT3Ic6op"
    return RedirectResponse(url=stripe_checkout_url)

# cancel
@app.post("/cancel-subscription")
async def cancel_subscription(request: Request):
    try:
        form_data = await request.json()
        subscription_id = form_data['subscription_id']
        subscription = stripe.Subscription.cancel(subscription_id, at_period_end=True)
        return subscription
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))