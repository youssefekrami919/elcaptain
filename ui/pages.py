import pandas as pd
import streamlit as st
from datetime import date, datetime
from core.rbac import require_role
from core.services.attendance_service import (
    ensure_daily_attendance,
    get_effective_attendance_date,
    list_daily_attendance,
    list_attendance_entries,
    move_to_checkout,
    move_to_done,
)
from core.services.employee_service import create_employee, list_employees, delete_employee
from core.services.finance_service import add_expense, add_revenue, list_finance
from core.services.user_service import create_user, list_users, rename_user, delete_user, update_user_password

def attendance_page(user: dict):
    st.subheader("Attendance")
    if not require_role(user, ("manager", "owner", "admin")):
        st.info("You don't have permission to manage attendance.")
        return

    def fmt_time(value):
        if not value:
            return "--"
        try:
            hour = value.strftime("%I").lstrip("0") or "12"
            return f"{hour}:{value.strftime('%M:%S')}"
        except Exception:
            text = str(value)
            if "T" in text and len(text) >= 19:
                hhmmss = text[11:19]
                try:
                    parsed = datetime.strptime(hhmmss, "%H:%M:%S")
                    hour = parsed.strftime("%I").lstrip("0") or "12"
                    return f"{hour}:{parsed.strftime('%M:%S')}"
                except Exception:
                    return hhmmss
            return text

    now = datetime.now()
    effective_date = get_effective_attendance_date(now)
    ensure_daily_attendance(now)

    st.markdown(
        """
        <style>
        .att-grid { display: grid; grid-template-columns: 1fr; gap: 18px; }
        .att-column {
            background: #0f131a;
            border: 1px solid #222a36;
            border-radius: 16px;
            padding: 14px 14px 6px;
            box-shadow: 0 10px 26px rgba(0,0,0,0.35);
        }
        .att-title {
            font-size: 20px;
            font-weight: 700;
            color: #d4af37;
            margin: 4px 0 12px;
        }
        .att-card {
            border: 1px solid #1f2733;
            border-radius: 12px;
            padding: 10px 12px;
            margin-bottom: 10px;
            background: linear-gradient(135deg, rgba(20,20,20,0.8), rgba(10,10,10,0.6));
        }
        .att-name { font-weight: 700; color: #f3e6b2; }
        .att-meta { color: #a7b0bf; font-size: 13px; margin-top: 6px; }
        @media (min-width: 1100px) {
            .att-grid { grid-template-columns: repeat(3, 1fr); }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    system_time = fmt_time(now)
    st.markdown(f"**Operational date:** {effective_date}      {system_time}")

    cols = st.columns(3)

    def render_card(r):
        check_in_str = fmt_time(r.get("check_in"))
        check_out_str = fmt_time(r.get("check_out"))
        phone = r.get("phone") or "--"
        st.markdown(
            f"""
            <div class="att-card">
                <div class="att-name">{r['full_name']} ({r['emp_id']})</div>
                <div class="att-meta">Phone: {phone}</div>
                <div class="att-meta">Date: {effective_date}</div>
                <div class="att-meta">Check-in: {check_in_str}</div>
                <div class="att-meta">Check-out: {check_out_str}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with cols[0]:
        st.markdown('<div class="att-column">', unsafe_allow_html=True)
        st.markdown('<div class="att-title">Attendance</div>', unsafe_allow_html=True)
        rows = list_daily_attendance(effective_date, "attendance")
        if not rows:
            st.info("No employees in Attendance.")
        for r in rows:
            render_card(r)
            if st.button("✔ Move to Checkout", key=f"att_{r['entry_id']}", use_container_width=True):
                move_to_checkout(r["entry_id"], user["username"])
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with cols[1]:
        st.markdown('<div class="att-column">', unsafe_allow_html=True)
        st.markdown('<div class="att-title">Checkout</div>', unsafe_allow_html=True)
        rows = list_daily_attendance(effective_date, "checkout")
        if not rows:
            st.info("No employees in Checkout.")
        for r in rows:
            render_card(r)
            if st.button("✔ Move to Done", key=f"out_{r['entry_id']}", use_container_width=True):
                move_to_done(r["entry_id"], user["username"])
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with cols[2]:
        st.markdown('<div class="att-column">', unsafe_allow_html=True)
        st.markdown('<div class="att-title">Done</div>', unsafe_allow_html=True)
        rows = list_daily_attendance(effective_date, "done")
        if not rows:
            st.info("No employees in Done.")
        for r in rows:
            render_card(r)
        st.markdown('</div>', unsafe_allow_html=True)

def finance_page(user: dict):
    st.subheader("Income & Expenses")
    is_owner = user["role"] in ("owner", "admin")
    is_manager = user["role"] == "manager"
    is_accountant = user["role"] == "accountant"

    if not (is_owner or is_manager or is_accountant):
        st.info("No permission.")
        return

    if is_owner or is_manager:
        st.markdown("### Add Entry")
        kind = st.selectbox("Type", ["Income", "Expense"])
        amount = st.number_input("Amount", min_value=0.01, value=100.0, step=10.0)
        desc = st.text_input("Description")
        dt = st.date_input("Date", value=date.today(), key="finance_date")
        tm = st.time_input("Time", value=datetime.now().time().replace(microsecond=0))
        if st.button("Add", type="primary"):
            if not desc.strip():
                st.error("Description is required.")
            else:
                time_str = tm.strftime("%H:%M:%S")
                if kind == "Expense":
                    add_expense("MAIN", float(amount), "expense", desc.strip(), str(dt), time_str, user["username"])
                else:
                    add_revenue("MAIN", float(amount), "income", desc.strip(), str(dt), time_str, user["username"])
                st.success("Saved.")

    st.markdown("---")
    st.markdown("### Records")
    with st.form("finance_filter"):
        filter_date = st.date_input("Filter by date", value=date.today())
        filter_kind = st.selectbox("Filter type", ["All", "Income", "Expense"])
        submitted = st.form_submit_button("Apply Filter")

    date_filter = str(filter_date) if submitted else None
    kind_filter = None
    if filter_kind == "Income":
        kind_filter = "revenue"
    elif filter_kind == "Expense":
        kind_filter = "expense"

    records = list_finance(kind=kind_filter, date_filter=date_filter, limit=1000)
    df = pd.DataFrame(records)
    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No records found.")

    if submitted:
        income_total = sum(r["amount"] for r in records if r["kind"] == "revenue")
        expense_total = sum(r["amount"] for r in records if r["kind"] == "expense")
        st.markdown(f"<div style='color:#2e7d32;font-weight:700'>Total income: {income_total:.2f}</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='color:#c62828;font-weight:700'>Total expenses: {expense_total:.2f}</div>", unsafe_allow_html=True)

def workers_page(user: dict):
    st.subheader("Worker Management")
    if not require_role(user, ("manager", "owner", "admin")):
        st.info("You don't have permission to add workers.")
        return

    st.markdown("### Add Worker")
    c1, c2 = st.columns(2)
    with c1:
        emp_id = st.text_input("Worker ID", placeholder="EMP-001")
        full_name = st.text_input("Full name")
    with c2:
        phone = st.text_input("Phone (optional)")
        email = st.text_input("Email (optional)")

    if st.button("Add Worker", type="primary"):
        if not emp_id.strip() or not full_name.strip():
            st.error("Worker ID and Full name are required.")
        else:
            row = create_employee({
                "emp_id": emp_id.strip(),
                "full_name": full_name.strip(),
                "phone": phone.strip() or None,
                "email": email.strip() or None,
                "job_role": "Worker",
                "salary": 0.0,
                "status": "active",
                "branch_code": "MAIN",
                "created_by": user["username"],
            })
            if not row:
                st.error("Worker ID already exists.")
            else:
                st.success("Worker added. They will appear in attendance starting next day at 8:00 AM.")

    st.markdown("---")
    st.markdown("### Worker List")
    st.dataframe(pd.DataFrame(list_employees()), use_container_width=True)

    st.markdown("---")
    st.markdown("### Delete Worker")
    del_emp = st.text_input("Worker ID to delete")
    if st.button("Delete Worker"):
        if not del_emp.strip():
            st.error("Worker ID is required.")
        else:
            row = delete_employee(del_emp.strip())
            if not row:
                st.error("Worker not found.")
            else:
                st.success("Worker deleted.")

def users_page(user: dict):
    st.subheader("User & Passwords")
    if not require_role(user, ("owner", "admin")):
        st.info("Only the Owner can manage credentials.")
        return

    st.markdown("### Create or Update User")
    c1, c2 = st.columns(2)
    with c1:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
    with c2:
        role = st.selectbox("Role", ["owner", "manager", "accountant"])
        emp_id = st.text_input("Employee ID (link)")
    if st.button("Save User", type="primary"):
        if not username.strip() or not password or len(password) < 6 or not emp_id.strip():
            st.error("Username, password (>=6), and Employee ID are required.")
        else:
            create_user(username.strip(), password, role, emp_id.strip(), user["username"])
            st.success("User saved.")

    st.markdown("---")
    st.markdown("### Rename Username")
    r1, r2 = st.columns(2)
    with r1:
        old_username = st.text_input("Current username")
    with r2:
        new_username = st.text_input("New username")
    if st.button("Rename"):
        if not old_username.strip() or not new_username.strip():
            st.error("Both usernames are required.")
        else:
            rename_user(old_username.strip(), new_username.strip(), user["username"])
            st.success("Username updated.")

    st.markdown("---")
    st.markdown("### Change Password")
    p1, p2 = st.columns(2)
    with p1:
        user_to_change = st.text_input("Username for password change")
    with p2:
        new_pass = st.text_input("New password", type="password")
    if st.button("Update Password"):
        if not user_to_change.strip() or not new_pass or len(new_pass) < 6:
            st.error("Username and new password (>=6) are required.")
        else:
            update_user_password(user_to_change.strip(), new_pass, user["username"])
            st.success("Password updated.")

    st.markdown("---")
    st.markdown("### Delete User")
    del_user = st.text_input("Username to delete")
    if st.button("Delete"):
        if not del_user.strip():
            st.error("Username required.")
        else:
            delete_user(del_user.strip(), user["username"])
            st.success("User deleted.")

    st.markdown("---")
    st.markdown("### Existing Users")
    st.dataframe(pd.DataFrame(list_users()), use_container_width=True)

def attendance_data_page(user: dict):
    st.subheader("Attendance Data")
    if not require_role(user, ("manager", "owner", "admin")):
        st.info("You don't have permission to view attendance data.")
        return

    employees = list_employees()
    emp_options = ["All"] + [f"{e['emp_id']} - {e['full_name']}" for e in employees]
    emp_map = {f"{e['emp_id']} - {e['full_name']}": e["emp_id"] for e in employees}

    c1, c2, c3 = st.columns(3)
    with c1:
        use_day = st.checkbox("Filter by day")
        day_filter = st.date_input("Day", value=date.today(), key="att_day") if use_day else None
    with c2:
        year = st.number_input("Year", min_value=2020, max_value=2100, value=datetime.now().year, step=1)
        month = st.number_input("Month", min_value=1, max_value=12, value=datetime.now().month, step=1)
    with c3:
        emp_choice = st.selectbox("Employee", emp_options)

    emp_id = None if emp_choice == "All" else emp_map.get(emp_choice)
    month_year = (int(year), int(month)) if month else None
    day = day_filter if day_filter else None

    if day:
        month_year = None

    rows = list_attendance_entries(day=day, month_year=month_year, emp_id=emp_id)
    df = pd.DataFrame(rows)
    if not df.empty:
        if "entry_id" in df.columns:
            df = df.drop(columns=["entry_id"])
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No attendance data found for the selected filters.")
