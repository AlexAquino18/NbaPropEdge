import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

supabase = create_client(
    os.getenv("VITE_SUPABASE_URL"),
    os.getenv("VITE_SUPABASE_PUBLISHABLE_KEY")
)

# Read the SQL file
with open("create_odds_history.sql", "r") as f:
    sql = f.read()

print("Creating odds_history table in Supabase...")
print("=" * 60)

try:
    # Execute the SQL
    result = supabase.rpc("exec_sql", {"query": sql}).execute()
    print("✅ Table created successfully!")
except Exception as e:
    print(f"Note: {e}")
    print("You may need to run this SQL manually in Supabase SQL Editor")
    
print("=" * 60)
