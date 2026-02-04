# Streamlit + Neo4j Multi-Branch Employee & Business Management System

A single **Streamlit** web UI (modern CSS) that connects to a centralized **Neo4j** graph database.

## Features (RBAC)
Roles: `admin`, `manager`, `accountant`, `employee`

- Auth: username/password (bcrypt) stored in Neo4j
- Branches: create/list (admin/manager)
- Employees: create/list/update (admin/manager), view (accountant/manager)
- Attendance: check-in/check-out, view logs (employee sees only self)
- Leaves: request (employee), approve/reject (manager/admin)
- Finance: expenses & revenues (accountant/manager/admin)
- Dashboard KPIs per branch

---

## Quick Start (Auto-start Neo4j via Docker + run Streamlit)

### Requirements
- Python 3.10+
- Docker Desktop installed and running

### Steps
```bash
cd streamlit_neo4j_mgmt
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/Mac: source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env   # Windows PowerShell: copy .env.example .env
# Edit .env if you want (password, ports, etc.)

python run.py
```

`run.py` will:
1) Start Neo4j Docker container (if not running)
2) Wait for Bolt to be ready
3) Launch Streamlit (`app.py`)

---

## If Neo4j is already running (Neo4j Desktop / Aura / server)
1) Update `.env` with your connection:
- Local: `NEO4J_URI=neo4j://localhost:7687`
- Aura: `NEO4J_URI=neo4j+s://xxxx.databases.neo4j.io`
2) Run:
```bash
streamlit run app.py
```

---

## Default admin login (auto-seeded on first run)
- username: **admin**
- password: **admin123**
- role: **admin**
Also seeds branch `MAIN` and employee `EMP-ADMIN`.

---

## Cypher schema
See `db_migrations/schema.cypher` (constraints, indexes, node labels, relationships).
The app applies these automatically at startup too.
