#!/usr/bin/env python3
"""Check current database schema and compare with API documentation."""

import os
import json
from sqlalchemy import create_engine, inspect, text
from dotenv import load_dotenv

load_dotenv()

# Get database connection string from environment
DB_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/fastapi_santri")

# Connect to database
engine = create_engine(DB_URL)
inspector = inspect(engine)

# Get all tables
tables = inspector.get_table_names()
print(f"\n✅ Total tables found: {len(tables)}\n")

schema_info = {}

for table_name in sorted(tables):
    columns = inspector.get_columns(table_name)
    schema_info[table_name] = {
        "columns": {}
    }
    
    print(f"\n📋 Table: {table_name}")
    print("=" * 80)
    
    for col in columns:
        col_type = str(col['type'])
        nullable = "NULL" if col['nullable'] else "NOT NULL"
        
        schema_info[table_name]["columns"][col['name']] = {
            "type": col_type,
            "nullable": col['nullable']
        }
        
        print(f"  - {col['name']:<30} {col_type:<25} {nullable}")

# Save to JSON file
with open('db_schema_actual.json', 'w') as f:
    json.dump(schema_info, f, indent=2, default=str)

print("\n\n✅ Schema exported to: db_schema_actual.json")

# Now compare with expected schema_context.json
print("\n\n" + "=" * 80)
print("COMPARISON WITH schema_context.json")
print("=" * 80)

with open('app/nl2sql/schema_context.json', 'r') as f:
    expected = json.load(f)['tables']

issues = []

for table_name in sorted(expected.keys()):
    if table_name not in schema_info:
        issues.append(f"❌ Table '{table_name}' MISSING from database")
        continue
    
    print(f"\n✅ {table_name}")
    expected_cols = expected[table_name]['columns']
    actual_cols = schema_info[table_name]['columns']
    
    for col_name in expected_cols.keys():
        if col_name not in actual_cols:
            issues.append(f"  ❌ Column '{table_name}.{col_name}' MISSING from database")
            print(f"    ❌ Column missing: {col_name}")
        else:
            print(f"    ✅ {col_name}")

# Check for extra columns in database
for table_name in schema_info.keys():
    if table_name in expected:
        expected_cols = set(expected[table_name]['columns'].keys())
        actual_cols = set(schema_info[table_name]['columns'].keys())
        extra = actual_cols - expected_cols
        for col in extra:
            print(f"    ℹ️  Extra column: {col}")

print("\n\n" + "=" * 80)
if issues:
    print("🔴 ISSUES FOUND:")
    for issue in issues:
        print(issue)
else:
    print("✅ All schema matches!")
