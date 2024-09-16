from fastapi import FastAPI, Request, HTTPException, APIRouter
import stripe
import threading
import time
from fastapi.responses import RedirectResponse
from apps.webui.models.users import Users
from flask import Flask, redirect, jsonify, request
import logging
import datetime

stripe.api_key = 'sk_test_51PpnBARwKnsYpxFvqOIE6TwPUD4MPyHODJVOcnlsqrJbD8U82aN98ZUwu5NmtXAHuMyQKjPORI089WcNT9d4du6300KTgiURES'
webhook_secret = 'whsec_45695097e5d997dbbb477f49b5f9224400d1b5764b9eb0acbd85e3a310a1a0be'

app = FastAPI()

customer_email = None
price = None
price_id = None
product = None
product_id = None
status = None
orvip = None
processing_subscription_update = False

log = logging.getLogger(__name__)


@app.post('/stripe')
async def stripe_webhook(request: Request):
    global customer_email, price, price_id, product, product_id, status, orvip , processing_subscription_update

    # log.warning("Received Stripe webhook")
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

    customer_email = data.get('customer_email')
    if not customer_email:
        customer_id = data.get('customer')
        if customer_id:
            customer = stripe.Customer.retrieve(customer_id)
            customer_email = customer.email

    if event_type == 'customer.subscription.created' or event_type == 'customer.subscription.updated':
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

        orvip = True
        print(f"new information: {price_id},{price},{product_id},{product},{orvip}")
        await save_to_database()

        if not processing_subscription_update:
            subscription_id = data.get('id')
            stripe.Subscription.modify(subscription_id, cancel_at_period_end=True)
            processing_subscription_update = True

    elif event_type == 'customer.subscription.deleted':
        price = None
        price_id = None
        product = None
        product_id = None
        orvip = False

        print(f"Subscription {data['id']} deleted. information: {price_id},{price},{product_id},{product}")
        await save_to_database()
        # add delete logic

    elif event_type == 'checkout.session.completed':
        status = data['payment_status']
        print(f"checkout.session.completed, {status}")
        print(f"new information: {price_id},{price},{product_id},{product}")
        # add more success logic

    elif event_type == 'customer.subscription.deleted':
        print(f"Subscription {data['id']} deleted")
        # add delete logic

    elif event_type == 'invoice.payment_succeeded':
        print("'invoice.payment_succeeded'")

    elif event_type == 'payment_method.attached':
        print("payment_method.attached")

    # else:
    #     print(f"Unhandled event type: {event_type}")

    return {"status": "success"}, 200


async def save_to_database():
    global customer_email, price, product, status, orvip
    print("save_to_database start")

    now = datetime.datetime.now()
    start_time = now.date()
    start_timestamp = now.timestamp()
    int_start_time = int(start_timestamp)
    end_time = now.date()

    try:
        user = Users.get_user_by_email(customer_email)

        if user:
            #如果orvip为true则表示更新,添加订阅
            if orvip:
                if product == "open webui ultra":
                    end_time = start_time + datetime.timedelta(days=365)
                elif product == "open webui pro":
                    end_time = start_time + datetime.timedelta(days=30)
                elif product == "open webui mini":
                    end_time = start_time + datetime.timedelta(days=7)
                end_datetime = datetime.datetime.combine(end_time, datetime.datetime.min.time())
                int_end_time = int(end_datetime.timestamp())
                updated_user = Users.update_user_by_id(user.id, {
                    "subscription_status": status,
                    "subscription_start_time": int_start_time,
                    "subscription_expiration":int_end_time,
                    "subscription_product":product,
                    "orvip": orvip,
                })

                if updated_user:
                    print(f"Successfully updated subscription for user: {updated_user.email}")
                else:
                    print(f"Failed to update subscription for user: {user.email}")
                print(f"data time: {start_time},{end_time}")
            #如果orvip为false则表示删除用户的订阅状态
            else:
                end_timestamp = now.timestamp()
                int_end_time = int(end_timestamp)
                updated_user = Users.update_user_by_id(user.id, {
                    "subscription_status": int_start_time,
                    "subscription_end_time": int_end_time,
                    "orvip": orvip,
                })
                if updated_user:
                    print(f"Successfully updated subscription for user: {updated_user.email}")
                else:
                    print(f"Failed to update subscription for user: {user.email}")
                print(f"data time: {start_time},{end_time}")
        else:
            # if product == "open webui ultra":
            #     end_time = start_time + timedelta(days=365)
            # elif product == "open webui pro":
            #     end_time = start_time + timedelta(days=30)
            # elif product == "open webui mini":
            #     end_time = start_time + timedelta(days=7)
            #
            # #这个添加新用户不知道写的对不对
            # new_user = Users.add_user(customer_email, status, start_time, end_time, product, orvip)
            #
            # if new_user:
            #     print(f"Successfully updated subscription for user: {new_user.email}")
            # else:
            #     print(f"Failed to update subscription for user: {user.email}")
            print("No user in database")
        print(f"database information:{orvip},{user.email},{product},{start_time},{end_time}")
    except Exception as e:
        print(f"Error when saving the subscription info: {e}")


@app.get("/subscribe/mini")
async def subscribe():
    log.warning("Received Stripe subscribe request")
    stripe_checkout_url = "https://buy.stripe.com/test_9AQfZ31oIbhL3Ic28a"
    return RedirectResponse(url=stripe_checkout_url)
@app.get("/subscribe/pro")
async def subscribe():
    log.warning("Received Stripe subscribe request")
    stripe_checkout_url = "https://buy.stripe.com/test_5kA149c3m3PjceI3cc"
    return RedirectResponse(url=stripe_checkout_url)
@app.get("/subscribe/ultra")
async def subscribe():
    log.warning("Received Stripe subscribe request")
    stripe_checkout_url = "https://buy.stripe.com/test_eVa5kpebudpT3Ic6op"
    return RedirectResponse(url=stripe_checkout_url)

# customer portal page
@app.get("/portal")
async def portal():
    log.warning("Test customer portal page")
    # customer_portal_url = "https://billing.stripe.com/p/login/test_bIYdRy2q67c65LWdQQ"
    # test with user email
    customer_portal_url = "https://billing.stripe.com/p/login/test_bIYdRy2q67c65LWdQQ?prefilled_email=1038959680@qq.com"
    return RedirectResponse(url=customer_portal_url)

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