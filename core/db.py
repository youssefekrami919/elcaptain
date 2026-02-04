from .config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD

_driver = None

def _load_graphdatabase():
    try:
        import neo4j as neo4j_pkg
    except Exception as e:
        raise ImportError(
            "Neo4j Python package is not available. Ensure `neo4j` is in requirements.txt "
            "and Streamlit Cloud installed dependencies successfully."
        ) from e

    if not hasattr(neo4j_pkg, "GraphDatabase"):
        module_path = getattr(neo4j_pkg, "__file__", None)
        module_version = getattr(neo4j_pkg, "__version__", None)
        raise ImportError(
            "Neo4j package loaded but GraphDatabase is missing. "
            f"module_path={module_path!r}, version={module_version!r}. "
            "This often happens when a local folder named `neo4j` shadows the driver, "
            "or when Streamlit cached an old build. Clear cache and redeploy."
        )

    return neo4j_pkg.GraphDatabase

def driver():
    global _driver
    if _driver is None:
        GraphDatabase = _load_graphdatabase()
        _driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    return _driver

def read(cypher: str, params: dict | None = None):
    d = driver()
    with d.session() as s:
        return s.execute_read(lambda tx: tx.run(cypher, params or {}).data())

def write(cypher: str, params: dict | None = None):
    d = driver()
    with d.session() as s:
        return s.execute_write(lambda tx: tx.run(cypher, params or {}).data())

def ensure_schema():
    statements = [
        "CREATE CONSTRAINT user_username_unique IF NOT EXISTS FOR (u:User) REQUIRE u.username IS UNIQUE",
        "CREATE CONSTRAINT branch_code_unique IF NOT EXISTS FOR (b:Branch) REQUIRE b.code IS UNIQUE",
        "CREATE CONSTRAINT employee_empid_unique IF NOT EXISTS FOR (e:Employee) REQUIRE e.emp_id IS UNIQUE",
        "CREATE CONSTRAINT attendance_day_date_unique IF NOT EXISTS FOR (d:AttendanceDay) REQUIRE d.date IS UNIQUE",
        "CREATE CONSTRAINT attendance_entry_id_unique IF NOT EXISTS FOR (a:AttendanceEntry) REQUIRE a.id IS UNIQUE",
        "CREATE CONSTRAINT audit_id_unique IF NOT EXISTS FOR (l:AuditLog) REQUIRE l.id IS UNIQUE",
        "CREATE INDEX attendance_by_time IF NOT EXISTS FOR (a:Attendance) ON (a.check_in, a.check_out)",
        "CREATE INDEX attendance_entry_by_date IF NOT EXISTS FOR (a:AttendanceEntry) ON (a.date, a.status)",
        "CREATE INDEX leave_by_status IF NOT EXISTS FOR (l:Leave) ON (l.status)",
        "CREATE INDEX expense_by_date IF NOT EXISTS FOR (x:Expense) ON (x.date)",
        "CREATE INDEX revenue_by_date IF NOT EXISTS FOR (r:Revenue) ON (r.date)",
    ]
    for st in statements:
        write(st)

def seed_admin_if_empty():
    rows = read("MATCH (u:User) RETURN count(u) AS c")
    if rows and rows[0]["c"] > 0:
        return

    write("""
    MERGE (b:Branch {code:'MAIN'})
    ON CREATE SET b.name='Main Branch', b.address='HQ', b.created_at=datetime()
    MERGE (e:Employee {emp_id:'EMP-ADMIN'})
    ON CREATE SET e.full_name='System Admin', e.job_role='Administrator', e.salary=0.0, e.status='active',
                  e.created_at=datetime()
    MERGE (e)-[:WORKS_AT]->(b)
    """)
    from .security import hash_pw
    pw_hash = hash_pw("admin123")
    write("""
    MATCH (e:Employee {emp_id:'EMP-ADMIN'})
    MERGE (u:User {username:'admin'})
    ON CREATE SET u.role='owner', u.password_hash=$pw_hash, u.created_at=datetime()
    ON MATCH SET u.role='owner', u.password_hash=$pw_hash
    MERGE (u)-[:ASSOCIATED_WITH]->(e)
    """, {"pw_hash": pw_hash})

def ensure_admin_account():
    from .security import hash_pw
    pw_hash = hash_pw("admin123")
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
    MERGE (u:User {username:'admin'})
    ON CREATE SET u.role='owner', u.password_hash=$pw_hash, u.created_at=datetime()
    ON MATCH SET u.role='owner', u.password_hash=$pw_hash
    MERGE (u)-[:ASSOCIATED_WITH]->(e)
    """, {"pw_hash": pw_hash})
