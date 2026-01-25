import os
from dotenv import load_dotenv
from supabase import create_client
import requests

load_dotenv()

url = os.getenv("VITE_SUPABASE_URL")
key = os.getenv("VITE_SUPABASE_PUBLISHABLE_KEY")

print("Reading migration file...")
with open("supabase/migrations/20260124000000_add_odds_history.sql", "r") as f:
    sql = f.read()

print("Applying migration to Supabase...")
print("=" * 60)

# Use the REST API to execute SQL
headers = {
    "apikey": key,
    "Authorization": f"Bearer {key}",
    "Content-Type": "application/json"
}

# Split SQL into individual statements
statements = [s.strip() for s in sql.split(";") if s.strip()]

for i, stmt in enumerate(statements, 1):
    print(f"Executing statement {i}/{len(statements)}...")
    
print("\n⚠️  Cannot execute SQL directly with anon key.")
print("Please run the SQL manually in Supabase dashboard:")
print("\n1. Go to: https://aimvwybpqhykuwiqddzu.supabase.co")
print("2. Click 'SQL Editor' in the sidebar")
print("3. Click 'New Query'")
print("4. Copy and paste the SQL from:")
print("   supabase/migrations/20260124000000_add_odds_history.sql")
print("5. Click 'Run' or press Ctrl+Enter")
print("\nOnce done, run: python upload_odds_to_supabase.py")
print("=" * 60)
