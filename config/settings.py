"""
Configuration loader for Pharmacy AI Chatbot
Supports both local development (.env) and Streamlit Cloud (secrets.toml)
"""

import os
import sys
import base64
import tempfile
from pathlib import Path

def load_configuration():
    """
    Load configuration from either Streamlit Cloud secrets or local .env file
    Sets environment variables for use by other modules
    """
    
    # Detect Streamlit Cloud environment
    # Only treat as cloud if ACTUALLY deployed to Streamlit Cloud
    # Not just because streamlit is running locally
    is_streamlit_cloud = (
        os.getenv('STREAMLIT_SHARING_MODE') is not None or
        os.getenv('STREAMLIT_SERVER_PORT') is not None or
        '/mount/src/' in os.getcwd()
    )
    
    if is_streamlit_cloud:
        print("🔐 Detected Streamlit Cloud environment")
        print("📥 Loading secrets from Streamlit Cloud...")
        
        try:
            import streamlit as st
            
            # Load Google API keys (flat format at root level)
            google_api_keys_loaded = 0
            for i in range(1, 10):  # Check up to 9 keys
                key_name = f'GOOGLE_API_KEY_{i}'
                if key_name in st.secrets:
                    os.environ[key_name] = st.secrets[key_name]
                    print(f"  ✅ Loaded {key_name}")
                    google_api_keys_loaded += 1
            
            if google_api_keys_loaded == 0:
                print("  ⚠️ No Google API keys found (GOOGLE_API_KEY_1, GOOGLE_API_KEY_2, etc.)")
            
            # Load Oracle credentials from [oracle] section
            if 'oracle' in st.secrets:
                if 'user' in st.secrets['oracle']:
                    os.environ['ORACLE_CLOUD_USER'] = st.secrets['oracle']['user']
                    print("  ✅ Loaded ORACLE_CLOUD_USER")
                
                if 'password' in st.secrets['oracle']:
                    os.environ['ORACLE_CLOUD_PASSWORD'] = st.secrets['oracle']['password']
                    print("  ✅ Loaded ORACLE_CLOUD_PASSWORD")
                
                if 'dsn' in st.secrets['oracle']:
                    os.environ['ORACLE_CLOUD_DSN'] = st.secrets['oracle']['dsn']
                    print("  ✅ Loaded ORACLE_CLOUD_DSN")
            else:
                print("  ⚠️ No [oracle] section found in secrets")
            
            # Load Oracle wallet from [oracle_wallet] section
            if 'oracle_wallet' in st.secrets:
                if 'wallet_password' in st.secrets['oracle_wallet']:
                    os.environ['ORACLE_WALLET_PASSWORD'] = st.secrets['oracle_wallet']['wallet_password']
                    print("  ✅ Loaded ORACLE_WALLET_PASSWORD")
                
                # Decode and save wallet file
                if 'cwallet_sso_base64' in st.secrets['oracle_wallet']:
                    try:
                        wallet_base64 = st.secrets['oracle_wallet']['cwallet_sso_base64']
                        wallet_bytes = base64.b64decode(wallet_base64)
                        
                        # Create temp directory for wallet
                        wallet_dir = tempfile.mkdtemp(prefix='oracle_wallet_')
                        wallet_path = os.path.join(wallet_dir, 'cwallet.sso')
                        
                        with open(wallet_path, 'wb') as f:
                            f.write(wallet_bytes)
                        
                        os.environ['ORACLE_WALLET_LOCATION'] = wallet_dir
                        print(f"  ✅ Decoded wallet to: {wallet_dir}")
                    except Exception as e:
                        print(f"  ❌ Failed to decode wallet: {e}")
            else:
                print("  ⚠️ No [oracle_wallet] section found in secrets")
            
            print("✅ Streamlit Cloud secrets loaded successfully")
            
            # Verify critical variables
            required_vars = ['GOOGLE_API_KEY_1', 'ORACLE_CLOUD_PASSWORD', 'ORACLE_CLOUD_DSN']
            missing_vars = [var for var in required_vars if var not in os.environ]
            
            if missing_vars:
                print(f"⚠️ Missing configuration: {', '.join(missing_vars)}")
            else:
                print("✅ All critical environment variables are set")
                
        except ImportError:
            print("❌ Streamlit not available - cannot load cloud secrets")
        except Exception as e:
            print(f"❌ Error loading Streamlit secrets: {e}")
    
    else:
        # Local development - load from .env file
        print("💻 Running in local development mode")
        print("📥 Loading from .env file...")
        
        try:
            from dotenv import load_dotenv
            
            # Look for .env file in config directory
            config_dir = Path(__file__).parent
            env_path = config_dir / '.env'
            
            if env_path.exists():
                load_dotenv(env_path)
                print(f"  ✅ Loaded environment variables from {env_path}")
                
                # Verify what was loaded
                google_keys_count = 0
                for i in range(1, 10):
                    if os.getenv(f'GOOGLE_API_KEY_{i}'):
                        google_keys_count += 1
                
                print(f"  ✅ Found {google_keys_count} Google API key(s)")
                
                if os.getenv('ORACLE_CLOUD_USER'):
                    print(f"  ✅ Found ORACLE_CLOUD_USER")
                if os.getenv('ORACLE_CLOUD_PASSWORD'):
                    print(f"  ✅ Found ORACLE_CLOUD_PASSWORD")
                if os.getenv('ORACLE_CLOUD_DSN'):
                    print(f"  ✅ Found ORACLE_CLOUD_DSN")
                    
                print("✅ Local configuration loaded successfully")
                
            else:
                print(f"  ⚠️ Warning: {env_path} not found!")
                print(f"  Current directory: {os.getcwd()}")
                print(f"  Config directory: {config_dir}")
                
        except ImportError:
            print("❌ python-dotenv not installed - cannot load .env file")
            print("   Install it with: pip install python-dotenv")

# Load configuration when this module is imported
load_configuration()
