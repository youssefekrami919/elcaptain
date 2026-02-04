from core.db import write, read
from core.security import hash_pw

print("=== Deleting old admin user ===")
write("""
MATCH (u:User {username:'admin'})
DETACH DELETE u
""")
print("✓ Old admin user deleted")

print("\n=== Creating new admin user ===")
pw_hash = hash_pw("admin123")
print(f"Password hash: {pw_hash[:20]}...")

write("""
MERGE (b:Branch {code:'MAIN'})
ON CREATE SET b.name='Main Branch', b.address='HQ', b.created_at=datetime()
MERGE (e:Employee {emp_id:'EMP-ADMIN'})
ON CREATE SET e.full_name='System Admin', e.job_role='Administrator', e.salary=0.0, e.status='active',
              e.created_at=datetime()
MERGE (e)-[:WORKS_AT]->(b)
""")

write("""
MATCH (e:Employee {emp_id:'EMP-ADMIN'})
CREATE (u:User {username:'admin', role:'admin', password_hash:$pw_hash, created_at:datetime()})
CREATE (u)-[:ASSOCIATED_WITH]->(e)
""", {"pw_hash": pw_hash})

print("✓ New admin user created")

print("\n=== Verifying ===")
rows = read("MATCH (u:User {username:'admin'}) RETURN u.username, u.role, u.password_hash")
if rows:
    print(f"Username: {rows[0]['username']}")
    print(f"Role: {rows[0]['role']}")
    print(f"Password hash: {rows[0]['password_hash'][:20]}...")
else:
    print("✗ User not found!")
