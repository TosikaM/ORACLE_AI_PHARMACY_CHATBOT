"""
test_database.py - Check if data actually exists in Oracle Cloud database
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment
config_dir = Path(__file__).parent / 'config'
env_path = config_dir / '.env'
load_dotenv(env_path)

import oracledb

print("="*70)
print("ORACLE CLOUD DATABASE TEST")
print("="*70)
print()

# Get credentials
user = os.getenv('ORACLE_CLOUD_USER')
password = os.getenv('ORACLE_CLOUD_PASSWORD')
dsn = os.getenv('ORACLE_CLOUD_DSN')
wallet_location = os.getenv('ORACLE_WALLET_LOCATION', 'database/wallet')

print(f"User: {user}")
print(f"DSN: {dsn}")
print(f"Wallet: {wallet_location}")
print()

try:
    # Connect to database
    print("Connecting to database...")
    connection = oracledb.connect(
        user=user,
        password=password,
        dsn=dsn,
        config_dir=wallet_location,
        wallet_location=wallet_location
    )
    print("✅ Connected successfully!")
    print()
    
    cursor = connection.cursor()
    
    # Test 1: Check if MEDICINES table exists
    print("TEST 1: Checking if MEDICINES table exists...")
    cursor.execute("""
        SELECT table_name 
        FROM user_tables 
        WHERE table_name = 'MEDICINES'
    """)
    
    result = cursor.fetchone()
    if result:
        print(f"✅ MEDICINES table exists!")
    else:
        print(f"❌ MEDICINES table NOT FOUND!")
        print("   The table might be in a different case or doesn't exist")
        print("   Let me check all tables...")
        cursor.execute("SELECT table_name FROM user_tables")
        tables = cursor.fetchall()
        print(f"   Found {len(tables)} tables:")
        for table in tables:
            print(f"   - {table[0]}")
    print()
    
    # Test 2: Count rows in MEDICINES table
    print("TEST 2: Counting rows in MEDICINES table...")
    try:
        cursor.execute("SELECT COUNT(*) FROM medicines")
        count = cursor.fetchone()[0]
        print(f"✅ Found {count} rows in MEDICINES table")
        
        if count == 0:
            print("❌ WARNING: Table exists but has NO DATA!")
            print("   You need to run the insert script again")
    except Exception as e:
        print(f"❌ Error counting rows: {str(e)}")
    print()
    
    # Test 3: Show all data
    print("TEST 3: Showing all data in MEDICINES table...")
    try:
        cursor.execute("""
            SELECT medicine_id, medicine_name, category_name, dosage_form, strength 
            FROM medicines 
            ORDER BY medicine_id
        """)
        
        rows = cursor.fetchall()
        
        if rows:
            print(f"Found {len(rows)} medicines:")
            print()
            for row in rows:
                print(f"ID: {row[0]}")
                print(f"Name: {row[1]}")
                print(f"Category: {row[2]}")
                print(f"Form: {row[3]}")
                print(f"Strength: {row[4]}")
                print("-" * 50)
        else:
            print("❌ No data found!")
    except Exception as e:
        print(f"❌ Error fetching data: {str(e)}")
    print()
    
    # Test 4: Test the same query the RAG engine uses
    print("TEST 4: Testing RAG engine query (search for 'paracetamol')...")
    try:
        cursor.execute("""
            SELECT 
                medicine_name,
                category_name,
                dosage_form,
                strength,
                manufacturer
            FROM medicines
            WHERE 
                LOWER(medicine_name) LIKE LOWER('%paracetamol%')
                OR LOWER(category_name) LIKE LOWER('%paracetamol%')
            ORDER BY medicine_name
            FETCH FIRST 5 ROWS ONLY
        """)
        
        rows = cursor.fetchall()
        
        if rows:
            print(f"✅ Found {len(rows)} results for 'paracetamol':")
            for row in rows:
                print(f"  - {row[0]} ({row[1]})")
        else:
            print("❌ No results found for 'paracetamol'")
            print("   This is why your chatbot can't find medicines!")
    except Exception as e:
        print(f"❌ Query error: {str(e)}")
    
    cursor.close()
    connection.close()
    
    print()
    print("="*70)
    print("TEST COMPLETE")
    print("="*70)
    
except Exception as e:
    print(f"❌ DATABASE ERROR: {str(e)}")
    print()
    print("Common issues:")
    print("1. Check ORACLE_CLOUD_PASSWORD is correct")
    print("2. Check ORACLE_CLOUD_DSN matches your wallet")
    print("3. Check wallet files are in database/wallet folder")
    print("4. Check database is RUNNING in Oracle Cloud Console")
