#!/usr/bin/env python3
"""
NovaLang Premium License CLI
Command-line tool for managing NovaLang premium licenses.
"""

import argparse
import json
import sys
from premium_license import license_manager, activate_license


def main():
    parser = argparse.ArgumentParser(description="NovaLang Premium License Manager")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Activate license command
    activate_parser = subparsers.add_parser('activate', help='Activate a premium license')
    activate_parser.add_argument('license_key', help='Your premium license key')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Check license status')
    
    # Features command
    features_parser = subparsers.add_parser('features', help='List available premium features')
    
    # Trial command
    trial_parser = subparsers.add_parser('trial', help='Start a free trial')
    
    args = parser.parse_args()
    
    if args.command == 'activate':
        print("🔑 Activating NovaLang Premium License...")
        result = activate_license(args.license_key)
        
        if result.get('valid'):
            print("✅ License activated successfully!")
            print(f"📊 Tier: {result.get('tier', 'unknown').title()}")
            print(f"📅 Expires: {result.get('expires', 'unknown')}")
            print(f"🌟 Features: {', '.join(result.get('features', []))}")
        else:
            print(f"❌ License activation failed: {result.get('error', 'Unknown error')}")
            sys.exit(1)
    
    elif args.command == 'status':
        print("📋 NovaLang License Status")
        print("=" * 30)
        
        license_info = license_manager.get_license_info()
        
        if license_info.get('valid'):
            print("✅ Premium license active")
            print(f"📊 Tier: {license_info.get('tier', 'unknown').title()}")
            print(f"📅 Expires: {license_info.get('expires', 'unknown')}")
            print(f"🌟 Features: {', '.join(license_info.get('features', []))}")
        else:
            print("❌ No valid license found")
            print("💡 Activate a license with: novalang-license activate YOUR_KEY")
            print("🎁 Get a free trial with: novalang-license trial")
    
    elif args.command == 'features':
        print("🌟 NovaLang Premium Features")
        print("=" * 35)
        
        features = {
            "🔍 Code Analysis": "Advanced static analysis and metrics",
            "⚡ Performance Tools": "Optimization and benchmarking",
            "🛡️  Security": "Encryption and secure operations", 
            "🌐 HTTP/API": "Advanced web requests and integrations",
            "🗄️  Database": "Multi-database support and ORM",
            "🤖 AI Assistance": "GPT-powered code generation",
            "⚙️  Debugging": "Advanced debugging and profiling",
            "👥 Team Features": "Collaboration and sharing tools"
        }
        
        license_info = license_manager.get_license_info()
        user_features = license_info.get('features', []) if license_info.get('valid') else []
        
        for feature, description in features.items():
            if any(f in user_features for f in ['advanced_stdlib', 'ai_assistance', 'team_features']):
                status = "✅"
            else:
                status = "🔒"
            print(f"{status} {feature}: {description}")
        
        if not user_features:
            print("\n💡 Unlock all features with NovaLang Pro!")
            print("🚀 Visit: https://novalang.dev/premium")
    
    elif args.command == 'trial':
        print("🎁 Starting NovaLang Premium Trial...")
        
        # Use demo license for trial
        trial_key = "NOVA-PRO-2025-DEMO"
        result = activate_license(trial_key)
        
        if result.get('valid'):
            print("✅ 30-day trial activated!")
            print("🌟 You now have access to all NovaLang Pro features!")
            print("📚 Try: analyze(), optimize(), benchmark(), and more!")
            print("💰 Upgrade anytime at: https://novalang.dev/premium")
        else:
            print("❌ Trial activation failed. Please contact support.")
    
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
