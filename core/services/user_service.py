from ..db import read, write
from ..security import hash_pw
from .audit_service import log_action

def create_user(username: str, password: str, role: str, emp_id: str, actor: str | None = None):
    pw_hash = hash_pw(password)
    rows = write("""
    MATCH (e:Employee {emp_id:$emp_id})
    MERGE (u:User {username:$username})
    ON CREATE SET u.role=$role, u.password_hash=$pw_hash, u.created_at=datetime()
    ON MATCH SET u.role=$role, u.password_hash=$pw_hash
    MERGE (u)-[:ASSOCIATED_WITH]->(e)
    RETURN u.username AS username, u.role AS role, e.emp_id AS emp_id
    """, {"username": username, "role": role, "pw_hash": pw_hash, "emp_id": emp_id})
    log_action("user_saved", actor or username, {"role": role, "emp_id": emp_id, "username": username})
    return rows[0]

def rename_user(old_username: str, new_username: str, actor: str):
    rows = write("""
    MATCH (u:User {username:$old})
    SET u.username=$new
    RETURN u.username AS username, u.role AS role
    """, {"old": old_username, "new": new_username})
    if rows:
        log_action("username_renamed", actor, {"from": old_username, "to": new_username})
    return rows[0] if rows else None

def update_user_password(username: str, password: str, actor: str):
    pw_hash = hash_pw(password)
    rows = write("""
    MATCH (u:User {username:$username})
    SET u.password_hash=$pw_hash
    RETURN u.username AS username, u.role AS role
    """, {"username": username, "pw_hash": pw_hash})
    if rows:
        log_action("password_updated", actor, {"username": username})
    return rows[0] if rows else None

def delete_user(username: str, actor: str):
    rows = write("""
    MATCH (u:User {username:$username})
    DETACH DELETE u
    RETURN $username AS username
    """, {"username": username})
    if rows:
        log_action("user_deleted", actor, {"username": username})
    return rows[0] if rows else None

def list_users():
    return read("""
    MATCH (u:User)-[:ASSOCIATED_WITH]->(e:Employee)
    RETURN u.username AS username, u.role AS role, e.emp_id AS emp_id
    ORDER BY u.username
    """)
