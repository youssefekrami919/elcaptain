from datetime import datetime, timedelta, date
from ..db import read, write
from .audit_service import log_action

def get_effective_attendance_date(now: datetime | None = None) -> date:
    now = now or datetime.now()
    day_start = now.replace(hour=8, minute=0, second=0, microsecond=0)
    if now < day_start:
        return now.date() - timedelta(days=1)
    return now.date()

def ensure_daily_attendance(now: datetime | None = None):
    now = now or datetime.now()
    effective_date = get_effective_attendance_date(now)
    params = {"date": str(effective_date)}
    exists = read("MATCH (d:AttendanceDay {date: date($date)}) RETURN count(d) AS c", params)
    if exists and exists[0]["c"] > 0:
        return {"date": effective_date, "created": False}

    write("""
    MERGE (d:AttendanceDay {date: date($date)})
    ON CREATE SET d.created_at=datetime(), d.opened_at=datetime()
    WITH d
    MATCH (e:Employee)
    CREATE (a:AttendanceEntry {
        id: randomUUID(),
        date: date($date),
        status: 'attendance',
        created_at: datetime()
    })
    CREATE (e)-[:HAS_ATTENDANCE]->(a)
    CREATE (d)-[:HAS_ENTRY]->(a)
    """, params)
    log_action("attendance_day_created", "system", {"date": str(effective_date)})
    return {"date": effective_date, "created": True}

def list_daily_attendance(att_date: date, status: str):
    return read("""
    MATCH (e:Employee)-[:HAS_ATTENDANCE]->(a:AttendanceEntry {date: date($date), status: $status})
    RETURN a.id AS entry_id, e.emp_id AS emp_id, e.full_name AS full_name, e.phone AS phone,
           a.check_in AS check_in, a.check_out AS check_out, a.date AS date
    ORDER BY e.full_name
    """, {"date": str(att_date), "status": status})

def list_attendance_entries(
    day: date | None = None,
    month_year: tuple[int, int] | None = None,
    emp_id: str | None = None,
):
    params = {}
    where = []
    cy = """
    MATCH (e:Employee)-[:HAS_ATTENDANCE]->(a:AttendanceEntry)
    """
    if emp_id:
        where.append("e.emp_id = $emp_id")
        params["emp_id"] = emp_id
    if day:
        where.append("a.date = date($day)")
        params["day"] = str(day)
    if month_year:
        year, month = month_year
        if month == 12:
            end_date = date(year + 1, 1, 1)
        else:
            end_date = date(year, month + 1, 1)
        start_date = date(year, month, 1)
        where.append("a.date >= date($start_date) AND a.date < date($end_date)")
        params["start_date"] = str(start_date)
        params["end_date"] = str(end_date)
    if where:
        cy += "WHERE " + " AND ".join(where) + " "
    cy += """
    RETURN a.id AS entry_id, e.emp_id AS emp_id, e.full_name AS full_name, e.phone AS phone,
           a.status AS status, a.date AS date, a.check_in AS check_in, a.check_out AS check_out
    ORDER BY a.date DESC, e.full_name
    """
    return read(cy, params)

def move_to_checkout(entry_id: str, actor: str):
    rows = write("""
    MATCH (a:AttendanceEntry {id:$id, status:'attendance'})
    SET a.status='checkout', a.check_in=datetime()
    WITH a
    MATCH (e:Employee)-[:HAS_ATTENDANCE]->(a)
    RETURN a.id AS entry_id, e.emp_id AS emp_id, e.full_name AS full_name,
           a.check_in AS check_in, a.check_out AS check_out, a.date AS date
    """, {"id": entry_id})
    if rows:
        log_action("attendance_check_in", actor, {"entry_id": entry_id})
        return rows[0]
    return None

def move_to_done(entry_id: str, actor: str):
    rows = write("""
    MATCH (a:AttendanceEntry {id:$id, status:'checkout'})
    SET a.status='done', a.check_out=datetime()
    WITH a
    MATCH (e:Employee)-[:HAS_ATTENDANCE]->(a)
    RETURN a.id AS entry_id, e.emp_id AS emp_id, e.full_name AS full_name,
           a.check_in AS check_in, a.check_out AS check_out, a.date AS date
    """, {"id": entry_id})
    if rows:
        log_action("attendance_check_out", actor, {"entry_id": entry_id})
        return rows[0]
    return None
