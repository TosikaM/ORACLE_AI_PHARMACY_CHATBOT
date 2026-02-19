"""
config/settings.py - Load configuration from .env (local) or st.secrets (cloud)
"""

import os
from pathlib import Path

def is_streamlit_cloud():
    """Detect if running in Streamlit Cloud."""
    return (
        os.getenv('STREAMLIT_SHARING_MODE') is not None or
        os.getenv('STREAMLIT_SERVER_PORT') is not None or
        'streamlit' in os.getenv('HOME', '').lower()
    )

def load_streamlit_secrets():
    """Load secrets from Streamlit Cloud and set as environment variables."""
    try:
        import streamlit as st
        
        print("🔐 Detected Streamlit Cloud environment")
        print("📥 Loading secrets from Streamlit Cloud...")
        
        # Load Google API keys
        if 'google_api' in st.secrets:
            google_secrets = st.secrets['google_api']
            for i in range(1, 10):  # Support up to 9 keys
                key_name = f'key_{i}'
                if key_name in google_secrets:
                    os.environ[f'GOOGLE_API_KEY_{i}'] = google_secrets[key_name]
                    print(f"  ✅ Loaded GOOGLE_API_KEY_{i}")
        
        # Load Oracle credentials
        if 'oracle' in st.secrets:
            oracle_secrets = st.secrets['oracle']
            if 'user' in oracle_secrets:
                os.environ['ORACLE_CLOUD_USER'] = oracle_secrets['user']
                print(f"  ✅ Loaded ORACLE_CLOUD_USER")
            if 'password' in oracle_secrets:
                os.environ['ORACLE_CLOUD_PASSWORD'] = oracle_secrets['password']
                print(f"  ✅ Loaded ORACLE_CLOUD_PASSWORD")
            if 'dsn' in oracle_secrets:
                os.environ['ORACLE_CLOUD_DSN'] = oracle_secrets['dsn']
                print(f"  ✅ Loaded ORACLE_CLOUD_DSN")
        
        # Load Oracle wallet configuration
        if 'oracle_wallet' in st.secrets:
            wallet_secrets = st.secrets['oracle_wallet']
            if 'wallet_password' in wallet_secrets:
                os.environ['ORACLE_WALLET_PASSWORD'] = wallet_secrets['wallet_password']
                print(f"  ✅ Loaded ORACLE_WALLET_PASSWORD")
            if 'cwallet_sso_base64' in wallet_secrets:
                # Decode wallet and save to temp file
                import base64
                import tempfile
                
                encoded_wallet = wallet_secrets['cwallet_sso_base64']
                wallet_bytes = base64.b64decode(encoded_wallet)
                
                # Create temp directory for wallet
                temp_dir = tempfile.mkdtemp()
                wallet_path = os.path.join(temp_dir, 'cwallet.sso')
                
                with open(wallet_path, 'wb') as f:
                    f.write(wallet_bytes)
                
                # Set wallet location to temp directory
                os.environ['ORACLE_WALLET_LOCATION'] = temp_dir
                print(f"  ✅ Decoded wallet to: {temp_dir}")
            elif 'wallet_location' in wallet_secrets:
                os.environ['ORACLE_WALLET_LOCATION'] = wallet_secrets['wallet_location']
        
        print("✅ All Streamlit Cloud secrets loaded successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error loading Streamlit secrets: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def load_local_env():
    """Load from .env file for local development."""
    try:
        from dotenv import load_dotenv
        
        config_dir = Path(__file__).parent
        env_path = config_dir / '.env'
        
        if env_path.exists():
            load_dotenv(env_path)
            print(f"✅ Loaded configuration from {env_path}")
            return True
        else:
            print(f"⚠️  Warning: {env_path} not found!")
            return False
            
    except ImportError:
        print("⚠️  python-dotenv not installed, skipping .env loading")
        return False

# Determine environment and load configuration
if is_streamlit_cloud():
    load_streamlit_secrets()
else:
    load_local_env()

# Verify critical variables are loaded
critical_vars = ['GOOGLE_API_KEY_1', 'ORACLE_CLOUD_PASSWORD', 'ORACLE_CLOUD_DSN']
missing = [var for var in critical_vars if not os.getenv(var)]

if missing:
    print(f"⚠️  Missing configuration: {', '.join(missing)}")
else:
    print("✅ All critical configuration loaded successfully")
