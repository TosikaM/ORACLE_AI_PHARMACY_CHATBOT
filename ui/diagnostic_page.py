"""
Database Connection Diagnostic Page
Run this to see what's happening with the database connection
"""

import streamlit as st
import os
import oracledb
import config.settings

st.title("🔍 Database Connection Diagnostic")

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

for key, value in env_vars.items():
    if value:
        if 'PASSWORD' in key or 'KEY' in key:
            st.success(f"✅ {key}: {'*' * 10} (set)")
        else:
            st.success(f"✅ {key}: {value}")
    else:
        st.error(f"❌ {key}: NOT SET")

st.write("## Database Connection Test")

try:
    user = os.getenv('ORACLE_CLOUD_USER')
    password = os.getenv('ORACLE_CLOUD_PASSWORD')
    dsn = os.getenv('ORACLE_CLOUD_DSN')
    wallet_password = os.getenv('ORACLE_WALLET_PASSWORD')
    wallet_location = os.getenv('ORACLE_WALLET_LOCATION')
    
    if not all([user, password, dsn, wallet_password, wallet_location]):
        st.error("❌ Missing required environment variables!")
        st.stop()
    
    st.info(f"Attempting connection to: {dsn}")
    st.info(f"User: {user}")
    st.info(f"Wallet location: {wallet_location}")
    
    # Try to connect
    connection = oracledb.connect(
        user=user,
        password=password,
        dsn=dsn,
        config_dir=wallet_location,
        wallet_location=wallet_location,
        wallet_password=wallet_password
    )
    
    st.success("✅ Database connection successful!")
    
    # Try a simple query
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM MEDICINES")
    count = cursor.fetchone()[0]
    
    st.success(f"✅ Found {count} medicines in database!")
    
    # Show a sample medicine
    cursor.execute("SELECT MEDICINE_ID, MEDICINE_NAME FROM MEDICINES WHERE ROWNUM <= 5")
    medicines = cursor.fetchall()
    
    st.write("### Sample Medicines:")
    for med_id, med_name in medicines:
        st.write(f"- {med_id}: {med_name}")
    
    cursor.close()
    connection.close()
    
except Exception as e:
    st.error(f"❌ Database connection failed!")
    st.error(f"Error type: {type(e).__name__}")
    st.error(f"Error message: {str(e)}")
    
    # Show more details
    st.write("### Detailed Error Information:")
    st.code(str(e))
    
    # Common errors and solutions
    st.write("### Possible Solutions:")
    
    error_str = str(e).lower()
    
    if "invalid username" in error_str or "invalid password" in error_str:
        st.warning("⚠️ **Wrong username or password**")
        st.write("Check your Oracle database credentials in Streamlit secrets")
    
    elif "cannot connect" in error_str or "connection refused" in error_str:
        st.warning("⚠️ **Cannot reach database**")
        st.write("This usually means:")
        st.write("1. Oracle Cloud Network ACL is blocking Streamlit Cloud IPs")
        st.write("2. DSN is incorrect")
        st.write("3. Database is not running")
    
    elif "wallet" in error_str:
        st.warning("⚠️ **Wallet issue**")
        st.write("Check:")
        st.write("1. Wallet password is correct")
        st.write("2. Base64 wallet string is complete")
        st.write("3. Wallet decoded successfully")
    
    else:
        st.warning("⚠️ **Unknown error**")
        st.write("Please share this error message for help")

st.write("---")
st.write("**Note:** If connection succeeds but chatbot says 'no medicines', the issue is in the RAG engine query logic, not the connection.")
