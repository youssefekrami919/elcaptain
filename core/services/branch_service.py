from ..db import read, write

def list_branches():
    return read("""MATCH (b:Branch) RETURN b.code AS code, b.name AS name, b.address AS address ORDER BY b.code""")

def upsert_branch(code: str, name: str, address: str | None):
    rows = write("""
    MERGE (b:Branch {code:$code})
    ON CREATE SET b.name=$name, b.address=$address, b.created_at=datetime()
    ON MATCH SET b.name=$name, b.address=$address
    RETURN b.code AS code, b.name AS name, b.address AS address
    """, {"code": code, "name": name, "address": address})
    return rows[0]
