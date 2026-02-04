CREATE CONSTRAINT user_username_unique IF NOT EXISTS
FOR (u:User) REQUIRE u.username IS UNIQUE;

CREATE CONSTRAINT branch_code_unique IF NOT EXISTS
FOR (b:Branch) REQUIRE b.code IS UNIQUE;

CREATE CONSTRAINT employee_empid_unique IF NOT EXISTS
FOR (e:Employee) REQUIRE e.emp_id IS UNIQUE;

CREATE CONSTRAINT attendance_day_date_unique IF NOT EXISTS
FOR (d:AttendanceDay) REQUIRE d.date IS UNIQUE;

CREATE CONSTRAINT attendance_entry_id_unique IF NOT EXISTS
FOR (a:AttendanceEntry) REQUIRE a.id IS UNIQUE;

CREATE CONSTRAINT audit_id_unique IF NOT EXISTS
FOR (l:AuditLog) REQUIRE l.id IS UNIQUE;

CREATE INDEX attendance_by_time IF NOT EXISTS
FOR (a:Attendance) ON (a.check_in, a.check_out);

CREATE INDEX attendance_entry_by_date IF NOT EXISTS
FOR (a:AttendanceEntry) ON (a.date, a.status);

CREATE INDEX leave_by_status IF NOT EXISTS
FOR (l:Leave) ON (l.status);

CREATE INDEX expense_by_date IF NOT EXISTS
FOR (x:Expense) ON (x.date);

CREATE INDEX revenue_by_date IF NOT EXISTS
FOR (r:Revenue) ON (r.date);

/*
Nodes:
User {username, role, password_hash, created_at}
Employee {emp_id, full_name, phone, email, job_role, salary, status, created_at}
Branch {code, name, address, created_at}
Attendance {attendance_id, check_in, check_out}
AttendanceDay {date, created_at, opened_at}
AttendanceEntry {id, date, status, check_in, check_out, created_at}
Leave {leave_id, from_date, to_date, reason, status, requested_at, approved_by, approved_at}
Expense {id, amount, category, description, date, time, created_by, created_at}
Revenue {id, amount, source, description, date, time, created_by, created_at}
AuditLog {id, action, actor, details, created_at}

Relationships:
(Employee)-[:WORKS_AT]->(Branch)
(User)-[:ASSOCIATED_WITH]->(Employee)
(Employee)-[:HAS_ATTENDANCE]->(Attendance)-[:AT_BRANCH]->(Branch)
(Employee)-[:HAS_ATTENDANCE]->(AttendanceEntry)<-[:HAS_ENTRY]-(AttendanceDay)
(Employee)-[:REQUESTED]->(Leave)
(User)-[:APPROVED]->(Leave)
(Branch)-[:HAS_EXPENSE]->(Expense)
(Branch)-[:HAS_REVENUE]->(Revenue)
(User)-[:CREATED]->(Expense|Revenue)
(User)-[:PERFORMED]->(AuditLog)
*/
