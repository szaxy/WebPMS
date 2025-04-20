import sys
import os
import psycopg2

def test_database_connection():
    print("Database Connection Test")
    print("=======================")
    
    # Hardcoded database connection parameters
    params = {
        'dbname': 'webpms',
        'user': 'postgres',
        'password': 'jaden123',  # Using the password from your .env file
        'host': '127.0.0.1',     # Using IP instead of hostname
        'port': '15432'
    }
    
    print("Connection parameters:")
    for key, value in params.items():
        if key != 'password':
            print(f"  {key}: {value}")
        else:
            print(f"  {key}: ****")
    
    print("\nAttempting to connect...")
    
    try:
        # Try connecting without any client_encoding
        conn = psycopg2.connect(**params)
        print("SUCCESS! Connected to the database.")
        conn.close()
        print("Connection closed successfully.")
        return True
    except Exception as e:
        print(f"ERROR: Could not connect to the database.")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        
        if isinstance(e, UnicodeDecodeError):
            print("\nUnicodeDecodeError details:")
            print(f"  Object: {e.object}")
            print(f"  Start: {e.start}")
            print(f"  End: {e.end}")
            print(f"  Reason: {e.reason}")
        
        print("\nTrying again with explicit encoding...")
        
        try:
            # Try connecting with explicit client_encoding
            params['client_encoding'] = 'UTF8'
            conn = psycopg2.connect(**params)
            print("SUCCESS! Connected with explicit UTF8 encoding.")
            conn.close()
            print("Connection closed successfully.")
            return True
        except Exception as e2:
            print(f"ERROR: Second attempt also failed.")
            print(f"Error type: {type(e2).__name__}")
            print(f"Error message: {str(e2)}")
            return False

if __name__ == "__main__":
    # Print Python version and system info
    print(f"Python version: {sys.version}")
    print(f"Executable: {sys.executable}")
    print(f"psycopg2 version: {psycopg2.__version__}")
    print()
    
    success = test_database_connection()
    
    print("\n=======================")
    if success:
        print("TEST RESULT: Connection successful!")
        print("Your database connection is working properly.")
    else:
        print("TEST RESULT: Connection failed!")
        print("Suggestions:")
        print("1. Verify PostgreSQL is running on port 15432")
        print("2. Check if the database 'webpms' exists")
        print("3. Ensure the username and password are correct")
        print("4. Try changing system locale to English (US)")
        print("5. Make sure all configuration files are saved with UTF-8 encoding")
    
    input("\nPress Enter to exit...") 