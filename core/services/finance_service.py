from ..db import read, write
from .audit_service import log_action
import uuid

def add_expense(branch_code: str, amount: float, category: str, description: str | None, date: str, time: str, created_by: str):
    xid = str(uuid.uuid4())
    rows = write("""
    MATCH (b:Branch {code:$branch_code})
    MERGE (u:User {username:$created_by})
    CREATE (x:Expense {
        id:$id, amount:$amount, category:$category, description:$description,
        date:date($date), time:time($time), created_by:$created_by, created_at:datetime()
    })
    CREATE (b)-[:HAS_EXPENSE]->(x)
    CREATE (u)-[:CREATED]->(x)
    RETURN x.id AS id, b.code AS branch_code, x.amount AS amount, 'expense' AS kind,
           x.category AS category_or_source, x.description AS description, x.date AS date,
           x.time AS time, x.created_by AS created_by, x.created_at AS created_at
    """, {"id": xid, "branch_code": branch_code, "amount": float(amount), "category": category,
           "description": description, "date": date, "time": time, "created_by": created_by})
    log_action("expense_added", created_by, {"id": xid, "amount": float(amount), "date": date, "time": time})
    return rows[0]

def add_revenue(branch_code: str, amount: float, source: str, description: str | None, date: str, time: str, created_by: str):
    rid = str(uuid.uuid4())
    rows = write("""
    MATCH (b:Branch {code:$branch_code})
    MERGE (u:User {username:$created_by})
    CREATE (r:Revenue {
        id:$id, amount:$amount, source:$source, description:$description,
        date:date($date), time:time($time), created_by:$created_by, created_at:datetime()
    })
    CREATE (b)-[:HAS_REVENUE]->(r)
    CREATE (u)-[:CREATED]->(r)
    RETURN r.id AS id, b.code AS branch_code, r.amount AS amount, 'revenue' AS kind,
           r.source AS category_or_source, r.description AS description, r.date AS date,
           r.time AS time, r.created_by AS created_by, r.created_at AS created_at
    """, {"id": rid, "branch_code": branch_code, "amount": float(amount), "source": source,
           "description": description, "date": date, "time": time, "created_by": created_by})
    log_action("revenue_added", created_by, {"id": rid, "amount": float(amount), "date": date, "time": time})
    return rows[0]

def list_finance(branch_code: str | None = None, kind: str | None = None, date_filter: str | None = None, limit: int = 200):
    params = {"limit": int(limit)}
    if date_filter:
        params["date"] = date_filter

    if kind == "expense":
        cy = """MATCH (b:Branch)-[:HAS_EXPENSE]->(x:Expense)"""
        if date_filter:
            cy += " WHERE x.date = date($date)"
        cy += """
        RETURN x.id AS id, b.code AS branch_code, x.amount AS amount, 'expense' AS kind,
               x.category AS category_or_source, x.description AS description, x.date AS date,
               x.time AS time, x.created_by AS created_by, x.created_at AS created_at
        ORDER BY x.date DESC, x.time DESC, x.created_at DESC LIMIT $limit"""
        rows = read(cy, params)
    elif kind == "revenue":
        cy = """MATCH (b:Branch)-[:HAS_REVENUE]->(r:Revenue)"""
        if date_filter:
            cy += " WHERE r.date = date($date)"
        cy += """
        RETURN r.id AS id, b.code AS branch_code, r.amount AS amount, 'revenue' AS kind,
               r.source AS category_or_source, r.description AS description, r.date AS date,
               r.time AS time, r.created_by AS created_by, r.created_at AS created_at
        ORDER BY r.date DESC, r.time DESC, r.created_at DESC LIMIT $limit"""
        rows = read(cy, params)
    else:
        cy = """MATCH (b:Branch)
        OPTIONAL MATCH (b)-[:HAS_EXPENSE]->(x:Expense)
        OPTIONAL MATCH (b)-[:HAS_REVENUE]->(r:Revenue)
        WITH b, x, r
        WITH collect(CASE WHEN x IS NULL THEN NULL ELSE {
            id:x.id, branch_code:b.code, amount:x.amount, kind:'expense',
            category_or_source:x.category, description:x.description, date:x.date,
            time:x.time, created_by:x.created_by, created_at:x.created_at
        } END) AS xs,
        collect(CASE WHEN r IS NULL THEN NULL ELSE {
            id:r.id, branch_code:b.code, amount:r.amount, kind:'revenue',
            category_or_source:r.source, description:r.description, date:r.date,
            time:r.time, created_by:r.created_by, created_at:r.created_at
        } END) AS rs
        WITH [i IN xs WHERE i IS NOT NULL] + [j IN rs WHERE j IS NOT NULL] AS items
        UNWIND items AS item"""
        if date_filter:
            cy += " WITH item WHERE item.date = date($date) RETURN item"
            cy += " ORDER BY item.date DESC, item.time DESC, item.created_at DESC LIMIT $limit"
            rows = read(cy, params)
            rows = [{
                "id": r["item"]["id"],
                "branch_code": r["item"]["branch_code"],
                "amount": r["item"]["amount"],
                "kind": r["item"]["kind"],
                "category_or_source": r["item"]["category_or_source"],
                "description": r["item"]["description"],
                "date": r["item"]["date"],
                "time": r["item"]["time"],
                "created_by": r["item"]["created_by"],
                "created_at": r["item"]["created_at"],
            } for r in rows]
        else:
            cy += """
            RETURN item.id AS id, item.branch_code AS branch_code, item.amount AS amount, item.kind AS kind,
                   item.category_or_source AS category_or_source, item.description AS description, item.date AS date,
                   item.time AS time, item.created_by AS created_by, item.created_at AS created_at
            ORDER BY item.date DESC, item.time DESC, item.created_at DESC LIMIT $limit"""
            rows = read(cy, params)
    if branch_code:
        rows = [r for r in rows if r["branch_code"] == branch_code]
    return rows[:limit]
