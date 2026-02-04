import streamlit as st
from ui.style import STYLE

st.set_page_config(page_title="ELCAPTAIN", page_icon="", layout="wide")
st.markdown(STYLE, unsafe_allow_html=True)

@st.cache_resource
def init_db():
    from core.db import ensure_schema, seed_admin_if_empty, ensure_admin_account
    ensure_schema()
    seed_admin_if_empty()
    ensure_admin_account()
    return True

def logout():
    for k in ["user","page","last_attendance_id","theme"]:
        st.session_state.pop(k, None)
    st.rerun()

def toggle_theme():
    current_theme = st.session_state.get("theme", "dark")
    st.session_state["theme"] = "light" if current_theme == "dark" else "dark"
    st.rerun()

def login_ui():
    from core.services.auth_service import login

    st.markdown(
        """
        <style>
        .login-wrap {
            max-width: 920px;
            margin: 0 auto;
        }
      
        .login-title {
            font-size: 34px;
            font-weight: 700;
            margin: 0;
            letter-spacing: 1.2px;
            color: #d4af37;
            text-align: center;
        }
        .login-title-box {
            background: #0a0a0a;
            border: 1px solid rgba(212,175,55,0.45);
            border-radius: 10px;
            padding: 14px 20px;
            display: inline-block;
            margin: 15px auto;
            text-align: center;
        }
        .login-divider {
            height: 1px;
            background: linear-gradient(90deg, transparent, rgba(212,175,55,0.55), transparent);
            margin: 20px 0 25px;
        }
        .center-content {
            display: flex;
            justify-content: center;
            align-items: center;
            flex-direction: column;
        }
        div[data-testid="stTabs"] { 
            max-width: 700px;
            margin-left: auto;
            margin-right: auto;
            background: linear-gradient(135deg, rgba(15,15,15,0.82), rgba(5,5,5,0.65));
            border: 1px solid rgba(212,175,55,0.35);
            border-radius: 18px;
            padding: 24px 22px 18px;
            box-shadow: 0 12px 30px rgba(0,0,0,0.35);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
        }
        div[data-testid="stTabs"] div[role="tablist"] {
            justify-content: center;
        }
        div[data-testid="stTabs"] button[role="tab"] {
            color: #d4af37;
        }
        div[data-testid="stTabs"] button[role="tab"] p {
            font-size: 18px;
            font-weight: 600;
        }
        div[data-testid="stTextInput"] label, div[data-testid="stPassword"] label {
            font-size: 16px;
            color: #ffffff;
        }
        div[data-testid="stTextInput"] input, div[data-testid="stPassword"] input {
            font-size: 16px;
            padding: 10px 12px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    
    st.markdown('<div class="login-wrap"><div class="login-card">', unsafe_allow_html=True)
    
  
    
    # Center title
    st.markdown('<div style="text-align: center;"><div class="login-title-box"><div class="login-title">ELCAPTAIN</div></div></div>', unsafe_allow_html=True)
    
    st.markdown('<div class="login-divider"></div>', unsafe_allow_html=True)
    
    # Tabs
    tabs = st.tabs(["Owner", "Manager", "Accountant"])

    def login_form(expected_roles: tuple[str, ...], default_page: str, tab_key: str):
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            username = st.text_input("Username", placeholder="admin", key=f"user_{tab_key}")
            password = st.text_input("Password", type="password", placeholder="admin123", key=f"pass_{tab_key}")
            if st.button("Sign in", type="primary", use_container_width=True, key=f"login_{tab_key}"):
                u = login(username.strip(), password)
                if not u:
                    st.error("Invalid username or password.")
                elif u["role"] not in expected_roles:
                    st.error("Unauthorized role for this tab.")
                else:
                    st.session_state["user"] = u
                    st.session_state["page"] = default_page
                    st.rerun()

    with tabs[0]:
        login_form(("owner", "admin"), "Attendance", "owner")
    with tabs[1]:
        login_form(("manager",), "Attendance", "manager")
    with tabs[2]:
        login_form(("accountant",), "Income & Expenses", "accountant")
    
    st.markdown("</div></div>", unsafe_allow_html=True)
def sidebar(user: dict):
    with st.sidebar:
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            st.image("barber_logo.png", width=150)
        st.markdown('<div id="sidebar-title">ELCAPTAIN</div>', unsafe_allow_html=True)

        st.divider()
        
        pages=["Attendance", "Attendance Data", "Income & Expenses", "Worker Management", "User & Passwords"]
        visible=[]
        is_owner = user["role"] in ("owner", "admin")
        for p in pages:
            if p == "User & Passwords" and not is_owner:
                continue
            if p == "Attendance Data" and user["role"] not in ("manager", "owner", "admin"):
                continue
            if p in ("Attendance", "Worker Management") and user["role"] not in ("manager", "owner", "admin"):
                continue
            if p == "Income & Expenses" and user["role"] not in ("manager", "accountant", "owner", "admin"):
                continue
            visible.append(p)
        
        current_page = st.session_state.get("page", "Attendance")
        
        for page in visible:
            if st.button(page, key=f"nav_{page.lower()}", help=f"Go to {page}", use_container_width=True):
                st.session_state["page"] = page
                st.rerun()
        
        st.divider()

        if st.button("Logout", use_container_width=True):
            logout()

def main():
    try:
        init_db()
    except Exception as e:
        st.error("Cannot connect to Neo4j. Check your .env and ensure Neo4j is running.")
        st.code(str(e))
        st.stop()

    from ui.pages import users_page, attendance_page, finance_page, workers_page, attendance_data_page

    user = st.session_state.get("user")
    if not user:
        login_ui()
        return

    sidebar(user)
    page = st.session_state.get("page","Attendance")
    st.title(page)

    if page == "Attendance":
        attendance_page(user)
    elif page == "Attendance Data":
        attendance_data_page(user)
    elif page == "Income & Expenses":
        finance_page(user)
    elif page == "Worker Management":
        workers_page(user)
    elif page == "User & Passwords":
        users_page(user)
    else:
        attendance_page(user)

if __name__ == "__main__":
    main()
