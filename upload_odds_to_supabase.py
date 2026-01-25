import os
import sqlite3
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

supabase = create_client(
    os.getenv("VITE_SUPABASE_URL"),
    os.getenv("VITE_SUPABASE_PUBLISHABLE_KEY")
)

print("=" * 60)
print("UPLOADING ODDS HISTORY FROM SQLITE TO SUPABASE")
print("=" * 60)

# Connect to SQLite
conn = sqlite3.connect("odds_history.db")
cursor = conn.cursor()

# Get all odds data
cursor.execute("SELECT * FROM odds_history ORDER BY recorded_at DESC")
rows = cursor.fetchall()
columns = [desc[0] for desc in cursor.description]

print(f"Found {len(rows)} odds records in SQLite")

# Transform to dict format for Supabase
odds_data = []
for row in rows:
    record = dict(zip(columns, row))
    # Remove the SQLite auto-increment id
    if "id" in record:
        del record["id"]
    odds_data.append(record)

# Upload in batches
batch_size = 100
total_uploaded = 0

for i in range(0, len(odds_data), batch_size):
    batch = odds_data[i:i+batch_size]
    try:
        result = supabase.table("odds_history").upsert(batch).execute()
        total_uploaded += len(batch)
        print(f"Uploaded batch {i//batch_size + 1}: {len(batch)} records")
    except Exception as e:
        print(f"Error uploading batch: {e}")

conn.close()

print("=" * 60)
print(f"UPLOAD COMPLETE: {total_uploaded} records")
print("=" * 60)
