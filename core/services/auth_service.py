from ..db import read
from .audit_service import log_action
from ..security import verify_pw

def get_user(username: str) -> dict | None:
    rows = read("""
    MATCH (u:User {username:$username})-[:ASSOCIATED_WITH]->(e:Employee)
    OPTIONAL MATCH (e)-[:WORKS_AT]->(b:Branch)
    RETURN u.username AS username, u.role AS role, u.password_hash AS password_hash,
           e.emp_id AS emp_id, e.full_name AS full_name,
           b.code AS branch_code, b.name AS branch_name
    """, {"username": username})
    return rows[0] if rows else None

def login(username: str, password: str) -> dict | None:
    u = get_user(username)
    if not u:
        return None
    if not verify_pw(password, u["password_hash"]):
        return None
    log_action("login_success", username, {})
    return {k:v for k,v in u.items() if k != "password_hash"}
