from ..db import read, write
import uuid

def request_leave(emp_id: str, from_date: str, to_date: str, reason: str):
    lid=str(uuid.uuid4())
    rows = write("""
    MATCH (e:Employee {emp_id:$emp_id})
    CREATE (l:Leave {leave_id:$lid, from_date:date($from_date), to_date:date($to_date), reason:$reason,
                    status:'pending', requested_at:datetime()})
    CREATE (e)-[:REQUESTED]->(l)
    RETURN l.leave_id AS leave_id, e.emp_id AS emp_id, l.from_date AS from_date, l.to_date AS to_date,
           l.reason AS reason, l.status AS status, l.requested_at AS requested_at,
           l.approved_by AS approved_by, l.approved_at AS approved_at
    """, {"emp_id": emp_id, "lid": lid, "from_date": from_date, "to_date": to_date, "reason": reason})
    return rows[0]

def list_leaves(status: str | None = None, emp_id: str | None = None, limit: int = 200):
    params={"limit": int(limit)}
    where=[]
    cy="MATCH (e:Employee)-[:REQUESTED]->(l:Leave) "
    if status:
        where.append("l.status=$status"); params["status"]=status
    if emp_id:
        where.append("e.emp_id=$emp_id"); params["emp_id"]=emp_id
    if where:
        cy += "WHERE " + " AND ".join(where) + " "
    cy += """RETURN l.leave_id AS leave_id, e.emp_id AS emp_id, l.from_date AS from_date, l.to_date AS to_date,
                    l.reason AS reason, l.status AS status, l.requested_at AS requested_at,
                    l.approved_by AS approved_by, l.approved_at AS approved_at
             ORDER BY l.requested_at DESC
             LIMIT $limit"""
    return read(cy, params)

def approve_leave(leave_id: str, username: str, action: str):
    new_status = "approved" if action == "approve" else "rejected"
    rows = write("""
    MATCH (l:Leave {leave_id:$leave_id})
    SET l.status=$new_status, l.approved_by=$username, l.approved_at=datetime()
    WITH l
    MATCH (e:Employee)-[:REQUESTED]->(l)
    MERGE (u:User {username:$username})
    MERGE (u)-[:APPROVED]->(l)
    RETURN l.leave_id AS leave_id, e.emp_id AS emp_id, l.from_date AS from_date, l.to_date AS to_date,
           l.reason AS reason, l.status AS status, l.requested_at AS requested_at,
           l.approved_by AS approved_by, l.approved_at AS approved_at
    """, {"leave_id": leave_id, "username": username, "new_status": new_status})
    return rows[0] if rows else None
