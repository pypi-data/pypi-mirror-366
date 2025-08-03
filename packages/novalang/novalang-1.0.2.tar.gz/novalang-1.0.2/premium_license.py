"""
NovaLang Premium License Manager
Handles premium feature licensing and validation.
"""

import hashlib
import json
import os
import time
from datetime import datetime, timedelta
from typing import Dict, Optional, Any
import requests


class LicenseManager:
    """Manages premium license validation and feature access."""
    
    def __init__(self):
        self.license_file = os.path.expanduser("~/.novalang_license")
        self.premium_server = "https://api.novalang.dev"  # Your premium server
        self._cached_license = None
        self._cache_expiry = None
    
    def validate_license(self, license_key: str = None) -> Dict[str, Any]:
        """Validate a premium license key."""
        if license_key:
            # Validate new license key
            return self._validate_online(license_key)
        else:
            # Check existing license
            return self._check_cached_license()
    
    def _validate_online(self, license_key: str) -> Dict[str, Any]:
        """Validate license key with premium server."""
        try:
            response = requests.post(
                f"{self.premium_server}/validate-license",
                json={"license_key": license_key, "version": "1.0.0"},
                timeout=10
            )
            
            if response.status_code == 200:
                license_data = response.json()
                if license_data.get("valid"):
                    # Cache the license
                    self._save_license(license_data)
                    return license_data
            
            return {"valid": False, "error": "Invalid license key"}
            
        except Exception as e:
            # Fallback to offline validation for demo
            return self._validate_offline(license_key)
    
    def _validate_offline(self, license_key: str) -> Dict[str, Any]:
        """Offline license validation (for demo purposes)."""
        # Simple demo validation - in production, use cryptographic signing
        demo_licenses = {
            "NOVA-PRO-2025-DEMO": {
                "valid": True,
                "tier": "pro",
                "expires": (datetime.now() + timedelta(days=30)).isoformat(),
                "features": ["advanced_stdlib", "debugger", "profiler", "ai_assistance"]
            },
            "NOVA-ENTERPRISE-DEMO": {
                "valid": True,
                "tier": "enterprise",
                "expires": (datetime.now() + timedelta(days=90)).isoformat(),
                "features": ["advanced_stdlib", "debugger", "profiler", "ai_assistance", 
                           "team_features", "priority_support", "custom_integrations"]
            }
        }
        
        license_data = demo_licenses.get(license_key)
        if license_data:
            self._save_license(license_data)
            return license_data
        
        return {"valid": False, "error": "Invalid license key"}
    
    def _check_cached_license(self) -> Dict[str, Any]:
        """Check cached license validity."""
        if not os.path.exists(self.license_file):
            return {"valid": False, "error": "No license found"}
        
        try:
            with open(self.license_file, 'r') as f:
                license_data = json.load(f)
            
            # Check expiry
            expires = datetime.fromisoformat(license_data.get("expires", ""))
            if datetime.now() > expires:
                return {"valid": False, "error": "License expired"}
            
            return license_data
            
        except Exception as e:
            return {"valid": False, "error": f"License validation failed: {e}"}
    
    def _save_license(self, license_data: Dict[str, Any]):
        """Save license data to cache file."""
        try:
            with open(self.license_file, 'w') as f:
                json.dump(license_data, f, indent=2)
        except Exception:
            pass  # Fail silently
    
    def has_feature(self, feature_name: str) -> bool:
        """Check if current license has a specific feature."""
        license_data = self.validate_license()
        if not license_data.get("valid"):
            return False
        
        features = license_data.get("features", [])
        return feature_name in features
    
    def get_license_info(self) -> Dict[str, Any]:
        """Get current license information."""
        return self.validate_license()


# Global license manager instance
license_manager = LicenseManager()


def premium_required(feature_name: str):
    """Decorator to require premium license for a function."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            if not license_manager.has_feature(feature_name):
                raise RuntimeError(
                    f"Premium feature '{feature_name}' requires a valid NovaLang Pro license. "
                    f"Visit https://novalang.dev/premium to upgrade."
                )
            return func(*args, **kwargs)
        return wrapper
    return decorator


def check_premium() -> bool:
    """Check if user has any premium license."""
    license_data = license_manager.validate_license()
    return license_data.get("valid", False)


def activate_license(license_key: str) -> Dict[str, Any]:
    """Activate a premium license."""
    return license_manager.validate_license(license_key)
