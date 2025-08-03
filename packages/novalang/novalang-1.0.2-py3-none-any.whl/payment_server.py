"""
NovaLang Payment Server
Flask backend for handling Stripe payments and license generation.
"""

from flask import Flask, request, jsonify, render_template_string, redirect
from flask_cors import CORS
import os
import json
import secrets
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)

# In production, store these in environment variables
STRIPE_PUBLISHABLE_KEY = "pk_test_your_publishable_key_here"
STRIPE_SECRET_KEY = "sk_test_your_secret_key_here" 
STRIPE_WEBHOOK_SECRET = "whsec_your_webhook_secret_here"

# Pricing configuration
PRICING = {
    "pro_monthly": {
        "price": 999,  # $9.99 in cents
        "currency": "usd",
        "interval": "month",
        "trial_days": 30
    },
    "pro_annual": {
        "price": 9900,  # $99 in cents
        "currency": "usd", 
        "interval": "year",
        "trial_days": 30
    },
    "enterprise_monthly": {
        "price": 9900,  # $99 in cents
        "currency": "usd",
        "interval": "month", 
        "trial_days": 30
    },
    "enterprise_annual": {
        "price": 99900,  # $999 in cents
        "currency": "usd",
        "interval": "year",
        "trial_days": 30
    },
    "pro_lifetime": {
        "price": 19900,  # $199 in cents
        "currency": "usd",
        "one_time": True
    }
}

@app.route('/')
def index():
    """Serve the pricing page."""
    with open('premium_page.html', 'r') as f:
        html_content = f.read()
    return html_content

@app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    """Create a Stripe checkout session."""
    try:
        data = request.get_json()
        tier = data.get('tier')
        billing = data.get('billing')
        
        price_key = f"{tier}_{billing}"
        if price_key not in PRICING:
            return jsonify({'error': 'Invalid pricing option'}), 400
        
        pricing = PRICING[price_key]
        
        # Mock Stripe checkout session creation
        # In production, use actual Stripe API
        session_id = f"cs_test_{secrets.token_hex(32)}"
        
        # For demo, return a mock URL
        checkout_url = f"/mock-checkout?session_id={session_id}&tier={tier}&billing={billing}"
        
        return jsonify({
            'session_id': session_id,
            'url': checkout_url
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/mock-checkout')
def mock_checkout():
    """Mock checkout page for testing."""
    session_id = request.args.get('session_id')
    tier = request.args.get('tier')
    billing = request.args.get('billing')
    
    price_key = f"{tier}_{billing}"
    pricing = PRICING.get(price_key, {})
    price_display = f"${pricing.get('price', 0) / 100:.2f}"
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>NovaLang Payment - Mock Checkout</title>
        <style>
            body {{ font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; }}
            .checkout {{ background: #f5f5f5; padding: 30px; border-radius: 10px; }}
            .btn {{ background: #667eea; color: white; padding: 15px 30px; border: none; border-radius: 5px; cursor: pointer; }}
            .btn:hover {{ background: #5a6fd8; }}
        </style>
    </head>
    <body>
        <div class="checkout">
            <h2>🔒 Secure Checkout</h2>
            <p><strong>Product:</strong> NovaLang {tier.title()} ({billing})</p>
            <p><strong>Price:</strong> {price_display}</p>
            <p><strong>Session ID:</strong> {session_id}</p>
            
            <form action="/process-payment" method="post">
                <input type="hidden" name="session_id" value="{session_id}">
                <input type="hidden" name="tier" value="{tier}">
                <input type="hidden" name="billing" value="{billing}">
                
                <h3>Payment Details (Mock)</h3>
                <p>
                    <label>Email:</label><br>
                    <input type="email" name="email" value="test@example.com" style="width: 100%; padding: 8px;">
                </p>
                <p>
                    <label>Card Number:</label><br>
                    <input type="text" value="4242 4242 4242 4242" disabled style="width: 100%; padding: 8px;">
                </p>
                <p>
                    <button type="submit" class="btn">Complete Payment (Mock)</button>
                </p>
            </form>
            
            <p style="margin-top: 20px; color: #666; font-size: 0.9rem;">
                This is a mock payment page for testing. In production, this would be handled by Stripe's secure checkout.
            </p>
        </div>
    </body>
    </html>
    """
    return html

@app.route('/process-payment', methods=['POST'])
def process_payment():
    """Process the mock payment and generate license."""
    try:
        session_id = request.form.get('session_id')
        tier = request.form.get('tier')
        billing = request.form.get('billing')
        email = request.form.get('email')
        
        # Generate license key
        license_key = generate_license_key(tier)
        
        # Store customer data (in production, use a database)
        customer_data = {
            'session_id': session_id,
            'email': email,
            'tier': tier,
            'billing': billing,
            'license_key': license_key,
            'created_at': datetime.now().isoformat(),
            'status': 'active'
        }
        
        # Save to mock database (JSON file for demo)
        save_customer_data(customer_data)
        
        return redirect(f'/success?license_key={license_key}')
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/success')
def success():
    """Payment success page."""
    license_key = request.args.get('license_key')
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Payment Successful - NovaLang Premium</title>
        <style>
            body {{ font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; text-align: center; }}
            .success {{ background: #d4edda; border: 1px solid #c3e6cb; color: #155724; padding: 30px; border-radius: 10px; }}
            .license-key {{ background: #f8f9fa; border: 2px dashed #667eea; padding: 20px; margin: 20px 0; font-family: monospace; font-size: 1.2rem; }}
            .btn {{ background: #667eea; color: white; padding: 15px 30px; border: none; border-radius: 5px; cursor: pointer; text-decoration: none; display: inline-block; }}
        </style>
    </head>
    <body>
        <div class="success">
            <h1>🎉 Payment Successful!</h1>
            <p>Thank you for purchasing NovaLang Premium!</p>
            
            <h3>Your License Key:</h3>
            <div class="license-key">{license_key}</div>
            
            <h3>Next Steps:</h3>
            <ol style="text-align: left; max-width: 400px; margin: 20px auto;">
                <li>Copy your license key above</li>
                <li>Open terminal/command prompt</li>
                <li>Run: <code>novalang-license activate {license_key}</code></li>
                <li>Start using premium features!</li>
            </ol>
            
            <p>
                <a href="/download" class="btn">Download NovaLang</a>
                <a href="/docs" class="btn">View Documentation</a>
            </p>
            
            <p style="margin-top: 30px; font-size: 0.9rem; color: #666;">
                Need help? Email us at support@novalang.dev
            </p>
        </div>
    </body>
    </html>
    """
    return html

@app.route('/api/validate-license', methods=['POST'])
def validate_license():
    """API endpoint to validate license keys."""
    try:
        data = request.get_json()
        license_key = data.get('license_key')
        
        # Load customer data
        customers = load_customer_data()
        
        for customer in customers:
            if customer.get('license_key') == license_key:
                return jsonify({
                    'valid': True,
                    'tier': customer.get('tier'),
                    'status': customer.get('status'),
                    'email': customer.get('email')
                })
        
        return jsonify({'valid': False})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/customer-info', methods=['POST'])
def get_customer_info():
    """Get customer information by license key."""
    try:
        data = request.get_json()
        license_key = data.get('license_key')
        
        customers = load_customer_data()
        
        for customer in customers:
            if customer.get('license_key') == license_key:
                return jsonify({
                    'success': True,
                    'customer': customer
                })
        
        return jsonify({'success': False, 'error': 'License not found'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def generate_license_key(tier: str) -> str:
    """Generate a unique license key."""
    timestamp = datetime.now().strftime("%Y%m")
    random_suffix = secrets.token_hex(4).upper()
    
    if tier == "pro":
        prefix = "NOVA-PRO"
    elif tier == "enterprise":
        prefix = "NOVA-ENT"
    else:
        prefix = "NOVA-STD"
    
    return f"{prefix}-{timestamp}-{random_suffix}"

def save_customer_data(customer_data: dict):
    """Save customer data to JSON file (mock database)."""
    try:
        if os.path.exists('customers.json'):
            with open('customers.json', 'r') as f:
                customers = json.load(f)
        else:
            customers = []
        
        customers.append(customer_data)
        
        with open('customers.json', 'w') as f:
            json.dump(customers, f, indent=2)
            
    except Exception as e:
        print(f"Error saving customer data: {e}")

def load_customer_data() -> list:
    """Load customer data from JSON file."""
    try:
        if os.path.exists('customers.json'):
            with open('customers.json', 'r') as f:
                return json.load(f)
        return []
    except Exception:
        return []

if __name__ == '__main__':
    print("🚀 NovaLang Payment Server starting...")
    print("📋 Available endpoints:")
    print("   GET  /                     - Pricing page")
    print("   POST /create-checkout-session - Create payment session")
    print("   GET  /mock-checkout        - Mock checkout page")
    print("   POST /process-payment      - Process mock payment")
    print("   GET  /success              - Payment success page")
    print("   POST /api/validate-license - Validate license key")
    print("   POST /api/customer-info    - Get customer info")
    print("\n🌐 Server running at: http://localhost:5000")
    
    app.run(debug=True, port=5000)

def main():
    """Entry point for novalang-server CLI command."""
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description='NovaLang Payment Server')
    parser.add_argument('--host', default='localhost', help='Host to bind to')
    parser.add_argument('--port', type=int, default=5000, help='Port to bind to')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--production', action='store_true', help='Run in production mode')
    
    args = parser.parse_args()
    
    if args.production:
        print("🚀 Starting NovaLang Payment Server in PRODUCTION mode")
        app.run(host=args.host, port=args.port, debug=False)
    else:
        print("🧪 Starting NovaLang Payment Server in DEVELOPMENT mode")
        app.run(host=args.host, port=args.port, debug=args.debug)
