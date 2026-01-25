#!/usr/bin/env python3
"""
Apply the odds_history migration to create the table for tracking line movements.
Run this once to set up the odds_history table.
"""
import os
from supabase import create_client, Client

# Initialize Supabase client
url = os.environ.get("VITE_SUPABASE_URL")
key = os.environ.get("VITE_SUPABASE_ANON_KEY")

if not url or not key:
    print("❌ Error: VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY environment variables must be set")
    exit(1)

supabase: Client = create_client(url, key)

# Read the migration file
migration_file = "supabase/migrations/20260124000000_add_odds_history.sql"
print(f"📖 Reading migration file: {migration_file}")

try:
    with open(migration_file, 'r') as f:
        migration_sql = f.read()
except FileNotFoundError:
    print(f"❌ Migration file not found: {migration_file}")
    exit(1)

print("🔧 Applying odds_history migration...")
print("=" * 60)

# Split the migration into individual statements
statements = [s.strip() for s in migration_sql.split(';') if s.strip()]

for i, statement in enumerate(statements, 1):
    if not statement:
        continue
    
    print(f"\n[{i}/{len(statements)}] Executing statement...")
    print(f"Preview: {statement[:100]}...")
    
    try:
        # Execute using Supabase RPC or direct SQL
        # Note: Supabase client doesn't support raw SQL execution directly
        # You need to use the Supabase Dashboard SQL Editor or CLI
        print("⚠️  This script requires the Supabase CLI or Dashboard SQL Editor")
        print("📋 Copy the migration SQL and run it in Supabase Dashboard > SQL Editor")
        print("\nMigration SQL:")
        print("=" * 60)
        print(migration_sql)
        print("=" * 60)
        break
    except Exception as e:
        print(f"❌ Error executing statement: {e}")
        exit(1)

print("\n✅ Please apply this migration using one of these methods:")
print("   1. Supabase Dashboard > SQL Editor (paste the SQL above)")
print("   2. Supabase CLI: supabase db push")
print("   3. Supabase CLI: supabase migration up")
