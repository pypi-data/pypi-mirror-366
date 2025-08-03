"""
NovaLang Payment Integration
Handles payment processing and license generation for NovaLang Premium.
"""

import stripe
import json
import secrets
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

# Configure Stripe (use test keys for development)
# stripe.api_key = "sk_test_your_stripe_secret_key_here"  # Replace with actual key
# Note: For testing without real keys, we'll mock the Stripe calls

class PaymentProcessor:
    """Handles Stripe payment processing for NovaLang Premium."""
    
    def __init__(self):
        self.prices = {
            "pro_monthly": "price_pro_monthly_id",      # $9.99/month
            "pro_annual": "price_pro_annual_id",        # $99/year  
            "enterprise_monthly": "price_ent_monthly_id", # $99/month
            "enterprise_annual": "price_ent_annual_id",   # $999/year
            "pro_lifetime": "price_pro_lifetime_id"      # $199 one-time
        }
    
    def create_customer(self, email: str, name: str = None) -> Dict[str, Any]:
        """Create a new Stripe customer."""
        try:
            customer = stripe.Customer.create(
                email=email,
                name=name,
                metadata={
                    'source': 'novalang',
                    'created_at': datetime.now().isoformat()
                }
            )
            return {
                'success': True,
                'customer_id': customer.id,
                'customer': customer
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def create_checkout_session(self, tier: str, billing: str, 
                               success_url: str, cancel_url: str,
                               customer_email: str = None) -> Dict[str, Any]:
        """Create a Stripe Checkout session for subscription."""
        try:
            price_key = f"{tier}_{billing}"
            if price_key not in self.prices:
                return {'success': False, 'error': 'Invalid tier/billing combination'}
            
            # For testing without real Stripe API keys, return mock session
            session_id = f"cs_test_{secrets.token_hex(16)}"
            
            return {
                'success': True,
                'session_id': session_id,
                'url': f"https://checkout.stripe.com/pay/{session_id}"
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def handle_webhook(self, payload: str, sig_header: str, 
                      webhook_secret: str) -> Dict[str, Any]:
        """Handle Stripe webhook events."""
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, webhook_secret
            )
            
            if event['type'] == 'checkout.session.completed':
                return self._handle_successful_payment(event['data']['object'])
            elif event['type'] == 'customer.subscription.created':
                return self._handle_subscription_created(event['data']['object'])
            elif event['type'] == 'customer.subscription.deleted':
                return self._handle_subscription_cancelled(event['data']['object'])
            elif event['type'] == 'invoice.payment_failed':
                return self._handle_payment_failed(event['data']['object'])
            
            return {'success': True, 'event': event['type']}
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _handle_successful_payment(self, session) -> Dict[str, Any]:
        """Handle successful payment completion."""
        try:
            # Extract metadata
            tier = session['metadata'].get('tier', 'pro')
            billing = session['metadata'].get('billing', 'monthly')
            customer_email = session.get('customer_details', {}).get('email')
            
            # Generate license key
            license_key = self._generate_license_key(tier)
            
            # Create license record (integrate with existing system)
            from premium_license import activate_license
            license_result = activate_license(license_key)
            
            # Store customer data
            customer_data = {
                'stripe_customer_id': session.get('customer'),
                'stripe_session_id': session['id'],
                'email': customer_email,
                'tier': tier,
                'billing': billing,
                'license_key': license_key,
                'activated_at': datetime.now().isoformat(),
                'payment_status': 'completed',
                'status': 'active'
            }
            
            return {
                'success': True,
                'license_key': license_key,
                'customer_data': customer_data
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _generate_license_key(self, tier: str) -> str:
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
    
    def get_customer_portal_url(self, customer_id: str, return_url: str) -> Dict[str, Any]:
        """Create customer portal session for subscription management."""
        try:
            session = stripe.billing_portal.Session.create(
                customer=customer_id,
                return_url=return_url
            )
            
            return {
                'success': True,
                'url': session.url
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }


class LicenseManager:
    """Manages license keys and customer data."""
    
    def __init__(self):
        self.customer_db = {}  # In production, use real database
    
    def store_customer(self, customer_data: Dict[str, Any]) -> bool:
        """Store customer data."""
        try:
            license_key = customer_data['license_key']
            self.customer_db[license_key] = customer_data
            return True
        except Exception:
            return False
    
    def get_customer_by_license(self, license_key: str) -> Optional[Dict[str, Any]]:
        """Get customer data by license key."""
        return self.customer_db.get(license_key)
    
    def get_customer_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get customer data by email."""
        for customer in self.customer_db.values():
            if customer.get('email') == email:
                return customer
        return None


# Example usage and testing
if __name__ == "__main__":
    processor = PaymentProcessor()
    
    # Example: Create checkout session for Pro monthly
    result = processor.create_checkout_session(
        tier="pro",
        billing="monthly", 
        success_url="https://novalang.dev/success",
        cancel_url="https://novalang.dev/cancel",
        customer_email="test@example.com"
    )
    
    print("Checkout session result:", result)
