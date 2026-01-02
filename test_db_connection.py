"""
Test PostgreSQL database connection
Run this to verify PostgreSQL is accessible from your local machine
"""
import os
from sqlalchemy import create_engine, text

# For local development, use localhost
DATABASE_URL = "postgresql://iau_admin:iau_secure_password_2024@localhost:5432/iau_portal"

print("Testing PostgreSQL connection...")
print(f"Database URL: {DATABASE_URL}\n")

try:
    # Create engine
    engine = create_engine(DATABASE_URL, echo=True)

    # Test connection
    with engine.connect() as connection:
        result = connection.execute(text("SELECT version();"))
        version = result.fetchone()[0]
        print(f"\n✅ SUCCESS! Connected to PostgreSQL")
        print(f"PostgreSQL Version: {version}\n")

except Exception as e:
    print(f"\n❌ ERROR: Could not connect to database")
    print(f"Error: {e}\n")
    print("Troubleshooting:")
    print("1. Make sure PostgreSQL container is running: docker ps")
    print("2. Start it if needed: docker-compose up -d postgres")
    print("3. Check credentials in .env.local match docker-compose.yml")
