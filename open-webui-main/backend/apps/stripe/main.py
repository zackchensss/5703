#! /usr/bin/env python3.6

"""
main.py
Stripe Sample.
Python 3.6 or newer required.
"""

import os
from flask import Flask, redirect, jsonify, json, request, current_app
import stripe
import webbrowser
import threading

# This is your test secret API key.
stripe.api_key = 'sk_test_51PpnBARwKnsYpxFvqOIE6TwPUD4MPyHODJVOcnlsqrJbD8U82aN98ZUwu5NmtXAHuMyQKjPORI089WcNT9d4du6300KTgiURES'
webhook_secret = 'whsec_45695097e5d997dbbb477f49b5f9224400d1b5764b9eb0acbd85e3a310a1a0be'

app = Flask(__name__,
            static_url_path='',
            static_folder='public')

### Add customer portal functionality to manage subscriptions page.
@app.route('/create-portal-session', methods=['POST'])
def create_portal_session():
    try:
        session_id = request.form.get('session_id')
        checkout_session = stripe.checkout.Session.retrieve(session_id)

        portal_session = stripe.billing_portal.Session.create(
            customer=checkout_session.customer,
            return_url=os.getenv('https://billing.stripe.com/p/login/test_bIYdRy2q67c65LWdQQ')  # 成功操作后用户将被重定向到这个URL
        )

        # 重定向用户到客户门户页面
        return redirect(portal_session.url, code=303)
    except Exception as e:
        return jsonify(error=str(e)), 400


@app.route('/api/webhook/stripe', methods=['POST'])
def stripe_webhook():
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
    except ValueError as e:
        return jsonify({'error': 'Invalid payload'}), 400
    except stripe.error.SignatureVerificationError as e:
        return jsonify({'error': 'Invalid signature'}), 400

    event_type = event['type']
    data = event['data']['object']

    if event_type == 'checkout.session.completed':
        print(f"Payment successful for session {data['id']}")
        # add more success

    elif event_type == 'customer.subscription.deleted':
        print(f"Subscription {data['id']} deleted")
        # add more delete

    else:
        print(f"Unhandled event type: {event_type}")

    return jsonify({}), 200

# cancel subscription
@app.route('/cancel-subscription', methods=['POST'])
def cancel_subscription():
    try:
        subscription_id = request.form['subscription_id']

        subscription = stripe.Subscription.cancel(subscription_id, at_period_end=True)
        return jsonify(subscription), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# create subscription
def open_browser():
    stripe_checkout_url = "https://buy.stripe.com/test_5kA149c3m3PjceI3cc"
    webbrowser.open_new(stripe_checkout_url)

if __name__ == '__main__':
    threading.Timer(1, open_browser).start()

    app.run(host='0.0.0.0', port=3000)