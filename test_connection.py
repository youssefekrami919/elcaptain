from neo4j import GraphDatabase
from core.config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD
from core.db import read, write, ensure_schema, seed_admin_if_empty
from core.security import hash_pw, verify_pw

print(f"NEO4J_URI: {NEO4J_URI}")
print(f"NEO4J_USER: {NEO4J_USER}")
print(f"NEO4J_PASSWORD: {NEO4J_PASSWORD[:10]}...")

print("\n=== Testing Connection ===")
try:
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    with driver.session() as session:
        result = session.run("RETURN 1")
        print("✓ Neo4j Connection successful!")
except Exception as e:
    print(f"✗ Connection failed: {e}")
    exit(1)

print("\n=== Ensuring Schema ===")
try:
    ensure_schema()
    print("✓ Schema ensured")
except Exception as e:
    print(f"✗ Schema error: {e}")

print("\n=== Seeding Admin User ===")
try:
    seed_admin_if_empty()
    print("✓ Admin user seeded")
except Exception as e:
    print(f"✗ Seed error: {e}")

print("\n=== Checking Users ===")
try:
    rows = read("MATCH (u:User) RETURN u.username, u.role, u.password_hash")
    print(f"Found {len(rows)} user(s):")
    for row in rows:
        print(f"  - Username: {row['username']}, Role: {row['role']}")
        print(f"    Password hash exists: {bool(row['password_hash'])}")
except Exception as e:
    print(f"✗ Query error: {e}")

print("\n=== Testing Login ===")
try:
    from core.services.auth_service import login
    result = login("admin", "admin123")
    if result:
        print(f"✓ Login successful: {result}")
    else:
        print("✗ Login failed")
except Exception as e:
    print(f"✗ Login error: {e}")
