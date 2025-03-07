import os
import sys
import psycopg2
from dotenv import load_dotenv

load_dotenv()


def test_db_connection():
    """Test connecting to the database directly using psycopg2"""
    db_url = os.environ.get("DATABASE_URL")

    # Display database URL (with password masked)
    masked_url = db_url
    if db_url and "@" in db_url:
        parts = db_url.split("@")
        if ":" in parts[0]:
            user_pass = parts[0].split(":")
            masked_url = f"{user_pass[0]}:****@{parts[1]}"

    print(f"Testing connection to: {masked_url}")

    try:
        # Try connecting directly
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()

        # Execute simple query
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"Connected successfully! PostgreSQL version: {version[0]}")

        # Test selecting from a table
        try:
            cursor.execute("SELECT COUNT(*) FROM auth_user;")
            user_count = cursor.fetchone()
            print(f"User count: {user_count[0]}")
        except Exception as table_error:
            print(f"Error querying table: {str(table_error)}")

        cursor.close()
        conn.close()
        return True

    except psycopg2.OperationalError as e:
        print(f"Connection error: {str(e)}")

        # Check if this is a connection parameter issue
        if "invalid connection option" in str(e):
            print(
                "\nPossible fix: Try removing extra connection parameters from DATABASE_URL"
            )
            print(
                "Use only: postgresql://username:password@host:port/dbname?sslmode=require"
            )

        return False
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return False


if __name__ == "__main__":
    success = test_db_connection()
    sys.exit(0 if success else 1)
