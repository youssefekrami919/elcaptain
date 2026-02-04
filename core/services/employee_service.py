from ..db import read, write
from .audit_service import log_action

def create_employee(p: dict):
    exists = read("MATCH (e:Employee {emp_id:$emp_id}) RETURN e.emp_id AS emp_id", {"emp_id": p.get("emp_id")})
    if exists:
        return None
    rows = write("""
    MATCH (b:Branch {code:$branch_code})
    CREATE (e:Employee {
        emp_id:$emp_id, full_name:$full_name, phone:$phone, email:$email,
        job_role:$job_role, salary:$salary, status:$status, created_at:datetime()
    })
    CREATE (e)-[:WORKS_AT]->(b)
    RETURN e.emp_id AS emp_id, e.full_name AS full_name, e.phone AS phone, e.email AS email,
           e.job_role AS job_role, e.salary AS salary, e.status AS status,
           b.code AS branch_code, b.name AS branch_name
    """, p)
    log_action("employee_created", p.get("created_by", "system"), {"emp_id": p.get("emp_id")})
    return rows[0]

def list_employees(branch_code: str | None = None):
    if branch_code:
        return read("""
        MATCH (e:Employee)-[:WORKS_AT]->(b:Branch {code:$branch_code})
        RETURN e.emp_id AS emp_id, e.full_name AS full_name, e.phone AS phone, e.email AS email,
               e.job_role AS job_role, e.salary AS salary, e.status AS status,
               b.code AS branch_code, b.name AS branch_name
        ORDER BY e.emp_id
        """, {"branch_code": branch_code})
    return read("""
    MATCH (e:Employee)-[:WORKS_AT]->(b:Branch)
    RETURN e.emp_id AS emp_id, e.full_name AS full_name, e.phone AS phone, e.email AS email,
           e.job_role AS job_role, e.salary AS salary, e.status AS status,
           b.code AS branch_code, b.name AS branch_name
    ORDER BY b.code, e.emp_id
    """)

def update_employee(emp_id: str, update: dict):
    params={"emp_id": emp_id}
    sets=[]
    for k,v in update.items():
        if v is None or v == "":
            continue
        if k == "branch_code":
            params["branch_code"]=v
        else:
            params[k]=v
            sets.append(f"e.{k} = ${k}")

    cy="MATCH (e:Employee {emp_id:$emp_id}) "
    if "branch_code" in params:
        cy += "MATCH (b:Branch {code:$branch_code}) WITH e,b OPTIONAL MATCH (e)-[r:WORKS_AT]->(:Branch) DELETE r MERGE (e)-[:WORKS_AT]->(b) WITH e,b "
    else:
        cy += "MATCH (e)-[:WORKS_AT]->(b:Branch) WITH e,b "
    if sets:
        cy += "SET " + ", ".join(sets) + " "
    cy += """RETURN e.emp_id AS emp_id, e.full_name AS full_name, e.phone AS phone, e.email AS email,
                     e.job_role AS job_role, e.salary AS salary, e.status AS status,
                     b.code AS branch_code, b.name AS branch_name"""
    rows = write(cy, params)
    return rows[0] if rows else None

def delete_employee(emp_id: str):
    rows = write("""
    MATCH (e:Employee {emp_id:$emp_id})
    DETACH DELETE e
    RETURN $emp_id AS emp_id
    """, {"emp_id": emp_id})
    return rows[0] if rows else None
