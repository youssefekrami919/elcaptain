from ..db import read

def branch_kpis(branch_code: str | None = None):
    params={}
    where=""
    if branch_code:
        where="WHERE b.code=$branch_code"
        params["branch_code"]=branch_code
    cy = f"""
    MATCH (b:Branch)
    {where}
    OPTIONAL MATCH (b)-[:HAS_REVENUE]->(r:Revenue)
    OPTIONAL MATCH (b)-[:HAS_EXPENSE]->(x:Expense)
    OPTIONAL MATCH (e:Employee)-[:WORKS_AT]->(b)
    OPTIONAL MATCH (e)-[:REQUESTED]->(l:Leave)
    OPTIONAL MATCH (e)-[:HAS_ATTENDANCE]->(a:Attendance)-[:AT_BRANCH]->(b)
    WITH b,
         sum(coalesce(r.amount,0)) AS total_rev,
         sum(coalesce(x.amount,0)) AS total_exp,
         count(DISTINCT e) AS emp_count,
         sum(CASE WHEN l.status='pending' THEN 1 ELSE 0 END) AS pending_leaves,
         sum(CASE WHEN date(a.check_in)=date() THEN 1 ELSE 0 END) AS today_checkins
    RETURN b.code AS branch_code, b.name AS branch_name,
           total_rev AS total_revenue, total_exp AS total_expense,
           (total_rev - total_exp) AS net,
           emp_count, pending_leaves, today_checkins
    ORDER BY b.code
    """
    return read(cy, params)
