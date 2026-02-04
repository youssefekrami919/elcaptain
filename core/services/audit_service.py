import json
from ..db import write

def log_action(action: str, actor: str, details: dict | None = None):
    payload = json.dumps(details or {}, ensure_ascii=False)
    write("""
    CREATE (l:AuditLog {
        id: randomUUID(),
        action: $action,
        actor: $actor,
        details: $details,
        created_at: datetime()
    })
    WITH l
    OPTIONAL MATCH (u:User {username: $actor})
    FOREACH (_ IN CASE WHEN u IS NULL THEN [] ELSE [1] END | CREATE (u)-[:PERFORMED]->(l))
    """, {"action": action, "actor": actor, "details": payload})
