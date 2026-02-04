from core.db import read, write

print("=== Raw User Data ===")
rows = read("MATCH (u:User) RETURN u")
print(f"Found {len(rows)} user(s)")
for row in rows:
    print(f"Row: {row}")
    print(f"User object: {row.get('u')}")
    user_obj = row.get('u')
    if user_obj:
        print(f"  Keys: {user_obj.keys() if hasattr(user_obj, 'keys') else 'N/A'}")
        if hasattr(user_obj, 'keys'):
            for k in user_obj.keys():
                print(f"    {k}: {user_obj[k]}")
