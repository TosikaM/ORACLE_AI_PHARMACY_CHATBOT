"""
encode_wallet.py - Convert wallet file to base64 for Streamlit Cloud

This script reads your cwallet.sso file and converts it to base64 text
so you can paste it into Streamlit Cloud secrets.

Run: python encode_wallet.py
"""

import base64
import os

print("="*70)
print("WALLET ENCODER FOR STREAMLIT CLOUD")
print("="*70)
print()

wallet_path = "database/wallet/cwallet.sso"

if os.path.exists(wallet_path):
    print(f"✅ Found wallet file: {wallet_path}")
    print(f"File size: {os.path.getsize(wallet_path)} bytes")
    print()
    
    with open(wallet_path, "rb") as f:
        wallet_bytes = f.read()
        encoded = base64.b64encode(wallet_bytes).decode('utf-8')
    
    print("✅ Wallet encoded successfully!")
    print()
    print("="*70)
    print("COPY THE TEXT BELOW:")
    print("="*70)
    print(encoded)
    print("="*70)
    print()
    print("INSTRUCTIONS:")
    print("1. Copy the long text above (the encoded wallet)")
    print("2. Go to Streamlit Cloud > App Settings > Secrets")
    print("3. Add this to your secrets under [oracle_wallet]:")
    print('   cwallet_sso_base64 = "PASTE_THE_ENCODED_TEXT_HERE"')
    print()
    
    # Also save to file for easy copying
    with open("wallet_encoded.txt", "w") as f:
        f.write(encoded)
    
    print("✅ Also saved to: wallet_encoded.txt")
    print("   You can open this file and copy from there too!")
    
else:
    print(f"❌ ERROR: Wallet file not found!")
    print(f"Expected location: {wallet_path}")
    print()
    print("Please make sure:")
    print("1. You extracted the wallet ZIP file")
    print("2. Wallet files are in: database/wallet/ folder")
    print("3. The cwallet.sso file exists")
