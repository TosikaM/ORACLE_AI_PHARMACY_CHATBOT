"""
database/connection.py
────────────────────────────────────────────────────────────────────
Oracle Autonomous Database Cloud Connection Module

This module connects to Oracle Autonomous Database in Oracle Cloud
Infrastructure (OCI) instead of a local installation. The key difference
is that cloud databases use a "wallet" file for secure authentication.

What is a wallet file?
  A wallet is a ZIP file containing security credentials that Oracle
  Cloud provides when you create a database. It includes certificates
  and connection information that prove you're authorized to access
  the database. Think of it like a digital key that unlocks your
  cloud database.

How this works:
  1. You download the wallet ZIP from Oracle Cloud Console
  2. You extract it to a folder called "wallet" in your project
  3. This module uses the wallet to establish secure connections
  4. All database queries go over encrypted internet connection to Oracle Cloud

This approach is simpler than local installation because Oracle manages
the database for you - no installation, no services to start, no
configuration beyond the initial wallet setup.
"""

import oracledb
import os
from typing import Optional
from contextlib import contextmanager


class OracleCloudConnection:
    """
    Manages connections to Oracle Autonomous Database in the cloud.
    
    This class handles all the complexity of wallet-based authentication
    and provides simple methods for executing queries against your
    cloud database.
    """
    
    _instance: Optional['OracleCloudConnection'] = None
    _connection_pool: Optional[oracledb.ConnectionPool] = None
    
    def __new__(cls):
        """
        Create a singleton instance.
        
        Singleton pattern ensures only one connection pool exists in
        your entire application, which is more efficient than creating
        multiple pools.
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """
        Initialize connection to Oracle Cloud database.
        
        This reads your wallet file and connection credentials from
        environment variables and establishes a connection pool to
        Oracle Autonomous Database.
        """
        if self._connection_pool is None:
            print("🔐 Initializing Oracle Cloud Database connection...")
            
            # Load configuration from environment variables
            # These come from your .env file in the config folder
            self.username = os.getenv("ORACLE_CLOUD_USER", "ADMIN")
            self.password = os.getenv("ORACLE_CLOUD_PASSWORD")
            self.dsn = os.getenv("ORACLE_CLOUD_DSN")
            
            # Wallet directory location
            # The wallet should be extracted to this folder
            wallet_location = os.getenv(
                "ORACLE_WALLET_LOCATION",
                os.path.join(os.path.dirname(__file__), "wallet")
            )
            
            # Validate required credentials
            if not self.password:
                raise ValueError(
                    "ORACLE_CLOUD_PASSWORD not found in environment variables.\n"
                    "Please set this in your config/.env file.\n\n"
                    "Example:\n"
                    "ORACLE_CLOUD_PASSWORD=your_admin_password_here"
                )
            
            if not self.dsn:
                raise ValueError(
                    "ORACLE_CLOUD_DSN not found in environment variables.\n"
                    "This should be the connection string from your wallet.\n\n"
                    "Example:\n"
                    "ORACLE_CLOUD_DSN=pharmacydb_high"
                )
            
            # Validate wallet exists
            if not os.path.exists(wallet_location):
                raise FileNotFoundError(
                    f"Oracle wallet not found at: {wallet_location}\n\n"
                    f"Please download your wallet from Oracle Cloud and extract it to:\n"
                    f"{wallet_location}\n\n"
                    f"Steps to get wallet:\n"
                    f"1. Go to Oracle Cloud Console\n"
                    f"2. Navigate to your Autonomous Database\n"
                    f"3. Click 'DB Connection'\n"
                    f"4. Click 'Download Wallet'\n"
                    f"5. Extract the ZIP file to the wallet folder"
                )
            
            try:
                # Configure wallet location for the Oracle client
                # This tells Oracle where to find the security credentials
                config_dir = wallet_location
                wallet_password = os.getenv("ORACLE_WALLET_PASSWORD")
                
                print(f"📁 Using wallet from: {wallet_location}")
                print(f"🔗 Connecting to DSN: {self.dsn}")
                
                # Create connection pool with wallet authentication
                # The pool maintains 2-5 connections ready for use
                self._connection_pool = oracledb.create_pool(
                    user=self.username,
                    password=self.password,
                    dsn=self.dsn,
                    config_dir=config_dir,  # Points to wallet directory
                    wallet_location=wallet_location,  # Also specify wallet
                    wallet_password=wallet_password,  # Wallet password if set
                    min=2,  # Minimum connections to keep open
                    max=5,  # Maximum connections allowed
                    increment=1  # How many to add when pool grows
                )
                
                print(f"✅ Connected to Oracle Cloud Database successfully!")
                print(f"   User: {self.username}")
                print(f"   Service: {self.dsn}")
                
                # Test the connection with a simple query
                with self.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT 'Connection test successful' FROM DUAL")
                    result = cursor.fetchone()
                    cursor.close()
                    print(f"✅ Connection test: {result[0]}")
            
            except Exception as e:
                error_msg = str(e)
                print(f"\n❌ Failed to connect to Oracle Cloud Database")
                print(f"Error: {error_msg}\n")
                
                # Provide helpful troubleshooting based on error
                if "wallet" in error_msg.lower():
                    print("💡 Troubleshooting Tips:")
                    print("  - Ensure wallet ZIP is extracted to database/wallet/")
                    print("  - Check that cwallet.sso file exists in wallet folder")
                    print("  - Verify ORACLE_WALLET_LOCATION in .env is correct")
                elif "password" in error_msg.lower():
                    print("💡 Troubleshooting Tips:")
                    print("  - Verify ORACLE_CLOUD_PASSWORD in .env is correct")
                    print("  - This is the ADMIN password you set when creating the database")
                elif "dsn" in error_msg.lower() or "service" in error_msg.lower():
                    print("💡 Troubleshooting Tips:")
                    print("  - Check ORACLE_CLOUD_DSN in .env matches tnsnames.ora")
                    print("  - Look in wallet/tnsnames.ora for available service names")
                    print("  - Common names: dbname_high, dbname_medium, dbname_low")
                else:
                    print("💡 Troubleshooting Tips:")
                    print("  - Ensure your Oracle Cloud database is running")
                    print("  - Check internet connectivity")
                    print("  - Verify all credentials in config/.env")
                
                raise
    
    @contextmanager
    def get_connection(self):
        """
        Get a database connection from the pool.
        
        Use this with Python's 'with' statement for automatic cleanup:
        
        Example:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM medicines")
                results = cursor.fetchall()
        
        The connection is automatically returned to the pool when the
        'with' block ends, even if an error occurs.
        
        Yields:
            oracledb.Connection: A cloud database connection
        """
        conn = self._connection_pool.acquire()
        try:
            yield conn
        finally:
            # Always return connection to pool
            self._connection_pool.release(conn)
    
    def execute_query(self, sql: str, params: dict = None):
        """
        Execute a SQL query and return results.
        
        This convenience method handles connection and cursor management
        for you, making it simple to execute queries.
        
        Args:
            sql: The SQL query to execute
            params: Optional dictionary of bind parameters
        
        Returns:
            list: List of tuples containing query results
        
        Example:
            # Simple query
            rows = db.execute_query("SELECT * FROM medicines")
            
            # Query with parameters (safer for user input)
            rows = db.execute_query(
                "SELECT * FROM medicines WHERE category_name = :cat",
                {"cat": "ANTIBIOTIC"}
            )
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            try:
                if params:
                    cursor.execute(sql, params)
                else:
                    cursor.execute(sql)
                
                # Fetch all results
                results = cursor.fetchall()
                return results
            
            finally:
                cursor.close()
    
    def execute_update(self, sql: str, params: dict = None):
        """
        Execute an INSERT, UPDATE, or DELETE statement.
        
        This method automatically commits the transaction after
        executing the SQL statement.
        
        Args:
            sql: The SQL statement to execute
            params: Optional dictionary of bind parameters
        
        Returns:
            int: Number of rows affected
        
        Example:
            # Insert new medicine
            db.execute_update(
                '''INSERT INTO medicines (medicine_name, category_name)
                   VALUES (:name, :cat)''',
                {"name": "Aspirin", "cat": "NSAID"}
            )
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            try:
                if params:
                    cursor.execute(sql, params)
                else:
                    cursor.execute(sql)
                
                # Commit the transaction
                conn.commit()
                
                # Return number of affected rows
                return cursor.rowcount
            
            finally:
                cursor.close()
    
    def close_pool(self):
        """
        Close the connection pool.
        
        Call this when your application shuts down to cleanly close
        all database connections.
        """
        if self._connection_pool:
            self._connection_pool.close()
            print("✅ Oracle Cloud connection pool closed")


# Create global instance for easy importing throughout the application
db_connection = OracleCloudConnection()


# Convenience functions for simple usage
def get_connection():
    """Get a database connection context manager."""
    return db_connection.get_connection()


def execute_query(sql: str, params: dict = None):
    """Execute a SELECT query and return results."""
    return db_connection.execute_query(sql, params)


def execute_update(sql: str, params: dict = None):
    """Execute an INSERT/UPDATE/DELETE and commit."""
    return db_connection.execute_update(sql, params)
