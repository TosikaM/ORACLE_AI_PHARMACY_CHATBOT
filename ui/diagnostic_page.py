"""
Database Connection Diagnostic Page
Run this to see what's happening with the database connection
"""

import streamlit as st
import os
import sys
import base64
import tempfile
from pathlib import Path
import oracledb

st.title("🔍 Database Connection Diagnostic")

# Load configuration inline
def load_configuration():
    """Load configuration from Streamlit Cloud secrets"""
    
    is_streamlit_cloud = (
        os.getenv('STREAMLIT_SHARING_MODE') is not None or
        os.getenv('STREAMLIT_SERVER_PORT') is not None or
        '/mount/src/' in os.getcwd()
    )
    
    if is_streamlit_cloud:
        st.info("🔐 Detected Streamlit Cloud environment")
        
        try:
            # Load Google API keys (flat format at root level)
            google_api_keys_loaded = 0
            for i in range(1, 10):
                key_name = f'GOOGLE_API_KEY_{i}'
                if key_name in st.secrets:
                    os.environ[key_name] = st.secrets[key_name]
                    google_api_keys_loaded += 1
            
            st.success(f"✅ Loaded {google_api_keys_loaded} Google API key(s)")
            
            # Load Oracle credentials from [oracle] section
            if 'oracle' in st.secrets:
                if 'user' in st.secrets['oracle']:
                    os.environ['ORACLE_CLOUD_USER'] = st.secrets['oracle']['user']
                    st.success("✅ Loaded ORACLE_CLOUD_USER")
                
                if 'password' in st.secrets['oracle']:
                    os.environ['ORACLE_CLOUD_PASSWORD'] = st.secrets['oracle']['password']
                    st.success("✅ Loaded ORACLE_CLOUD_PASSWORD")
                
                if 'dsn' in st.secrets['oracle']:
                    os.environ['ORACLE_CLOUD_DSN'] = st.secrets['oracle']['dsn']
                    st.success("✅ Loaded ORACLE_CLOUD_DSN")
            else:
                st.error("❌ No [oracle] section found in secrets")
            
            # Load Oracle wallet from [oracle_wallet] section
            if 'oracle_wallet' in st.secrets:
                if 'wallet_password' in st.secrets['oracle_wallet']:
                    os.environ['ORACLE_WALLET_PASSWORD'] = st.secrets['oracle_wallet']['wallet_password']
                    st.success("✅ Loaded ORACLE_WALLET_PASSWORD")
                
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
                        st.success(f"✅ Decoded wallet to: {wallet_dir}")
                    except Exception as e:
                        st.error(f"❌ Failed to decode wallet: {e}")
            else:
                st.error("❌ No [oracle_wallet] section found in secrets")
                
        except Exception as e:
            st.error(f"❌ Error loading Streamlit secrets: {e}")
    else:
        st.warning("💻 Running in local mode (not Streamlit Cloud)")

# Load configuration
st.write("## Loading Configuration")
load_configuration()

st.write("---")
st.write("## Environment Variables Check")

# Check if environment variables are set
env_vars = {
    "GOOGLE_API_KEY_1": os.getenv('GOOGLE_API_KEY_1'),
    "GOOGLE_API_KEY_2": os.getenv('GOOGLE_API_KEY_2'),
    "ORACLE_CLOUD_USER": os.getenv('ORACLE_CLOUD_USER'),
    "ORACLE_CLOUD_PASSWORD": os.getenv('ORACLE_CLOUD_PASSWORD'),
    "ORACLE_CLOUD_DSN": os.getenv('ORACLE_CLOUD_DSN'),
    "ORACLE_WALLET_PASSWORD": os.getenv('ORACLE_WALLET_PASSWORD'),
    "ORACLE_WALLET_LOCATION": os.getenv('ORACLE_WALLET_LOCATION'),
}

all_set = True
for key, value in env_vars.items():
    if value:
        if 'PASSWORD' in key or 'KEY' in key:
            st.success(f"✅ {key}: {'*' * 10} (set)")
        else:
            st.success(f"✅ {key}: {value}")
    else:
        st.error(f"❌ {key}: NOT SET")
        all_set = False

if not all_set:
    st.error("❌ Some environment variables are missing! Check your secrets configuration.")
    st.stop()

st.write("---")
st.write("## Database Connection Test")

try:
    user = os.getenv('ORACLE_CLOUD_USER')
    password = os.getenv('ORACLE_CLOUD_PASSWORD')
    dsn = os.getenv('ORACLE_CLOUD_DSN')
    wallet_password = os.getenv('ORACLE_WALLET_PASSWORD')
    wallet_location = os.getenv('ORACLE_WALLET_LOCATION')
    
    st.info(f"**Attempting connection to:** {dsn}")
    st.info(f"**User:** {user}")
    st.info(f"**Wallet location:** {wallet_location}")
    
    with st.spinner("Connecting to database..."):
        # Try to connect
        connection = oracledb.connect(
            user=user,
            password=password,
            dsn=dsn,
            config_dir=wallet_location,
            wallet_location=wallet_location,
            wallet_password=wallet_password
        )
    
    st.success("🎉 **Database connection successful!**")
    
    # Try a simple query
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM MEDICINES")
    count = cursor.fetchone()[0]
    
    st.success(f"✅ **Found {count} medicines in database!**")
    
    # Show a sample medicine
    cursor.execute("SELECT MEDICINE_ID, MEDICINE_NAME FROM MEDICINES WHERE ROWNUM <= 5")
    medicines = cursor.fetchall()
    
    st.write("### Sample Medicines:")
    for med_id, med_name in medicines:
        st.write(f"- **{med_id}**: {med_name}")
    
    cursor.close()
    connection.close()
    
    st.write("---")
    st.success("✅ **DIAGNOSIS: Database connection is working perfectly!**")
    st.info("If the chatbot says 'no medicines listed', the issue is in the RAG engine query logic, not the database connection.")
    
except Exception as e:
    st.error(f"❌ **Database connection failed!**")
    st.error(f"**Error type:** {type(e).__name__}")
    st.error(f"**Error message:** {str(e)}")
    
    # Show more details
    st.write("### Detailed Error Information:")
    st.code(str(e))
    
    # Common errors and solutions
    st.write("---")
    st.write("### 🔧 Possible Solutions:")
    
    error_str = str(e).lower()
    
    if "invalid username" in error_str or "invalid password" in error_str or "ora-01017" in error_str:
        st.warning("⚠️ **Wrong username or password**")
        st.write("**Solution:** Check your Oracle database credentials in Streamlit Cloud secrets")
        st.write("Make sure the password in [oracle] section matches your actual database password")
    
    elif "cannot connect" in error_str or "connection refused" in error_str or "ora-12170" in error_str or "ora-12541" in error_str:
        st.warning("⚠️ **Cannot reach database**")
        st.write("**This usually means:**")
        st.write("1. ⚠️ **Oracle Cloud Network ACL is blocking Streamlit Cloud IPs** (most common)")
        st.write("2. DSN is incorrect")
        st.write("3. Database is not running")
        st.write("")
        st.write("**Solution for #1:**")
        st.write("- Go to Oracle Cloud Console")
        st.write("- Navigate to your Autonomous Database")
        st.write("- Click **Network** → **Access Control List**")
        st.write("- Change from 'Secure access from allowed IPs only' to **'Secure access from everywhere'**")
        st.write("- Or add Streamlit Cloud IP ranges to the allowlist")
    
    elif "wallet" in error_str or "ora-28759" in error_str:
        st.warning("⚠️ **Wallet issue**")
        st.write("**Check:**")
        st.write("1. Wallet password is correct")
        st.write("2. Base64 wallet string is complete (not truncated)")
        st.write("3. Wallet decoded successfully")
    
    elif "ora-12154" in error_str:
        st.warning("⚠️ **TNS name not found**")
        st.write("**Solution:** Check your DSN value - should be like 'pharmacydb_high'")
    
    else:
        st.warning("⚠️ **Unknown error**")
        st.write("Please share this error message for further diagnosis")

st.write("---")
st.write("**After diagnosis, change the main file back to:** `ui/chatbot_ui.py`")
