from core.db import read

print("=== Verifying user with object notation ===")
rows = read("MATCH (u:User {username:'admin'}) RETURN u")
if rows:
    user = rows[0]['u']
    print(f"Username: {user['username']}")
    print(f"Role: {user['role']}")
    print(f"Password hash: {user['password_hash'][:20]}...")
    
    # Test login
    from core.services.auth_service import login
    result = login("admin", "admin123")
    if result:
        print("\n✓ Login test PASSED!")
        print(f"Logged in user: {result}")
    else:
        print("\n✗ Login test FAILED!")
else:
    print("✗ User not found!")
