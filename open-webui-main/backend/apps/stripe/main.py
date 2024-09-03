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

    if event_type in ['customer.subscription.created', 'customer.subscription.updated']:
        if 'items' in data:
            price_id = data['items']['data'][0]['price']['id']
            product_id = data['items']['data'][0]['price']['product']

            if price_id == "price_1PsP8yRwKnsYpxFv5d2FxFUI":
                price = "99.99"
            elif price_id == "price_1PrbewRwKnsYpxFvTZXXC1JK":
                price = "9.99"
            else:
                price = "error"

            if product_id == "prod_QjsurwseJK95jp":
                product = "open webui ultra"
            elif product_id == "prod_Qj3merrWlM46hw":
                product = "open webui pro"
            else:
                product = "error"
        else:
            print("No items found in the subscription data.")

    if event_type == 'checkout.session.completed':
        status = data['payment_status']
        await save_to_database()
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
    global customer_email, price, price_id, product, product_id, status
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
    stripe_checkout_url = "https://buy.stripe.com/test_eVa5kpebudpT3Ic6op"
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
# import os
# from datetime import time
#
# from flask import Flask, redirect, jsonify, request
# import stripe
# import webbrowser
# import threading
# from apps.webui.models.users import Users
#
# # This is your test secret API key.
# stripe.api_key = 'sk_test_51PpnBARwKnsYpxFvqOIE6TwPUD4MPyHODJVOcnlsqrJbD8U82aN98ZUwu5NmtXAHuMyQKjPORI089WcNT9d4du6300KTgiURES'
# webhook_secret = 'whsec_45695097e5d997dbbb477f49b5f9224400d1b5764b9eb0acbd85e3a310a1a0be'
#
# app = Flask(__name__,
#             static_url_path='',
#             static_folder='public')
#
#
# # 定义全局变量
# customer_email = None
# price = None
# price_id = None
# product = None
# product_id = None
# status = None
#
# ### Add customer portal functionality to manage subscriptions page.
# @app.route('/create-portal-session', methods=['POST'])
# def create_portal_session():
#
#     try:
#         session_id = request.form.get('session_id')
#         checkout_session = stripe.checkout.Session.retrieve(session_id)
#
#         portal_session = stripe.billing_portal.Session.create(
#             customer=checkout_session.customer,
#             return_url=os.getenv('https://billing.stripe.com/p/login/test_bIYdRy2q67c65LWdQQ')  # 成功操作后用户将被重定向到这个URL
#         )
#
#         return redirect(portal_session.url, code=303)
#     except Exception as e:
#         return jsonify(error=str(e)), 400
#
#
# @app.route('/api/webhook/stripe', methods=['POST'])
# def stripe_webhook():
#     global customer_email, price, price_id, product, product_id, status
#
#     payload = request.get_data(as_text=True)
#     sig_header = request.headers.get('Stripe-Signature')
#
#     try:
#         event = stripe.Webhook.construct_event(
#             payload, sig_header, webhook_secret
#         )
#     except ValueError as e:
#         return jsonify({'error': 'Invalid payload'}), 400
#     except stripe.error.SignatureVerificationError as e:
#         return jsonify({'error': 'Invalid signature'}), 400
#
#     event_type = event['type']
#     data = event['data']['object']
#
#     customer_email = data.get('customer_email')
#     if not customer_email:
#         customer_id = data.get('customer')
#         if customer_id:
#             customer = stripe.Customer.retrieve(customer_id)
#             customer_email = customer.email
#
#     if event_type == 'customer.subscription.created' or event_type == 'customer.subscription.updated':
#         if 'items' in data:
#             price_id = data['items']['data'][0]['price']['id']
#             product_id = data['items']['data'][0]['price']['product']
#
#             if price_id == "price_1PsP8yRwKnsYpxFv5d2FxFUI":
#                 price = "99.99"
#             elif price_id == "price_1PrbewRwKnsYpxFvTZXXC1JK":
#                 price = "9.99"
#             else:
#                 price = "error"
#
#             if product_id == "prod_QjsurwseJK95jp":
#                 product = "open webui ultra"
#             elif product_id == "prod_Qj3merrWlM46hw":
#                 product = "open webui pro"
#             else:
#                 product = "error"
#
#         else:
#             print("No items found in the subscription data.")
#
#     if event_type == 'checkout.session.completed':
#         status = data['payment_status']
#         save_to_database()
#         print("checkout.session.completed")
#         # add more success
#
#     elif event_type == 'customer.subscription.deleted':
#         print(f"Subscription {data['id']} deleted")
#         # add more delete
#
#     elif event_type == 'invoice.payment_succeeded':
#         print("'invoice.payment_succeeded'")
#
#     elif event_type == 'payment_method.attached':
#         print("payment_method.attached")
#
#
#     else:
#         print(f"Unhandled event type: {event_type}")
#
#
#     return jsonify({'status': 'success'}), 200
#
# ###存到数据库
# def save_to_database():
#     global customer_email, price, price_id, product, product_id, status
#     try:
#         # get the user
#         user = Users.get_user_by_email(customer_email)
#         if user:
#             user.subscription_status = status
#             # decide the expire time based on different product
#             if product == "open webui ultra":
#                 user.subscription_expiration = int(time.time()) + 365 * 24 * 60 * 60  # yearyly
#             elif product == "open webui pro":
#                 user.subscription_expiration = int(time.time()) + 30 * 24 * 60 * 60  # monthly
#             else:
#                 return
#             # user.product = product
#             # user.price = price
#             # update the database
#             Users.update_user_by_id(user.id, {
#                 "subscription_status": user.subscription_status,
#                 "subscription_expiration": user.subscription_expiration,
#                 # "product": user.product,
#                 # "price": user.price
#             })
#     except Exception as e:
#         print(f"Wrong when updating the subscription status: {e}")
#
#
# # cancel subscription
# @app.route('/cancel-subscription', methods=['POST'])
# def cancel_subscription():
#     try:
#         subscription_id = request.form['subscription_id']
#
#         subscription = stripe.Subscription.cancel(subscription_id, at_period_end=True)
#         return jsonify(subscription), 200
#     except Exception as e:
#         return jsonify({'error': str(e)}), 400
#
# # create subscription
# def open_browser():
# ###    stripe_checkout_url = "https://buy.stripe.com/test_5kA149c3m3PjceI3cc"
#     stripe_checkout_url = "https://buy.stripe.com/test_eVa5kpebudpT3Ic6op"
#     webbrowser.open_new(stripe_checkout_url)
#
# if __name__ == '__main__':
#     threading.Timer(1, open_browser).start()
#
#     app.run(host='0.0.0.0', port=3000)