import streamlit as st
import sys
from pathlib import Path

# Put the repo root on sys.path so `from frontend.views import ...` resolves
# regardless of the directory streamlit was launched from.
sys.path.insert(0, str(Path(__file__).parent.parent))

# Configure page
st.set_page_config(
    page_title="ATS Resume Scorer",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Auth state. Populated by username/password authentication.
# Session values are populated after a successful login.
for key, default in [
    ("access_token", None),
    ("refresh_token", None),
    ("user_id", None),       # Supabase auth user id (uuid); also used by api_client
    ("username", st.session_state.get("user_email")),
    ("auth_error", None),
]:
    if key not in st.session_state:
        st.session_state[key] = default

#Load custom CSS
def load_css():
    try:
        css_path = Path(__file__).parent / 'assets' / 'styles.css'
        with open(css_path, 'r') as f:
            return f'<style>{f.read()}</style>'
    except FileNotFoundError:
        return ''

st.markdown(load_css(), unsafe_allow_html=True)

# Initialize session state for view management
if 'current_view' not in st.session_state:
    st.session_state.current_view = 'landing'

# Sidebar navigation
with st.sidebar:
    st.markdown("## Navigation")
    
    if st.button("🏠 Home", use_container_width=True):
        st.session_state.current_view = 'landing'
        st.rerun()
    
    if st.button("🎯 ATS Scorer", use_container_width=True):
        st.session_state.current_view = 'scorer'
        st.rerun()
    
    if st.button("📊 History", use_container_width=True):
        st.session_state.current_view = 'history'
        st.rerun()
    
    if st.button("📚 Resources", use_container_width=True):
        st.session_state.current_view = 'resources'
        st.rerun()
    
    st.markdown("---")
    st.markdown("### 👤 Account")

    from frontend.services import supabase_client

    if st.session_state.access_token:
        # Signed-in state: show username + sign-out button.
        st.caption(f"Signed in as **{st.session_state.username}**")
        if st.button("Sign out", use_container_width=True):
            supabase_client.sign_out()
            for k in ("access_token", "refresh_token", "user_id", "username", "user_email"):
                st.session_state[k] = None
            st.rerun()
    else:
        # Signed-out state: username/password login or account creation.
        if st.session_state.auth_error:
            st.error(st.session_state.auth_error)
            st.session_state.auth_error = None

        tab_login, tab_signup = st.tabs(["Login", "Sign up"])

        with tab_login:
            with st.form("login_form", clear_on_submit=False):
                username = st.text_input("Username", key="login_username")
                password = st.text_input("Password", type="password", key="login_pw")
                submitted = st.form_submit_button("Login", use_container_width=True)
            if submitted:
                result = supabase_client.sign_in_with_password(username, password)
                if "error" in result:
                    st.session_state.auth_error = result["error"]
                else:
                    st.session_state.access_token  = result["access_token"]
                    st.session_state.refresh_token = result["refresh_token"]
                    st.session_state.user_id       = result["user_id"]
                    st.session_state.username      = result["username"]
                st.rerun()

        with tab_signup:
            with st.form("signup_form", clear_on_submit=False):
                username = st.text_input(
                    "Username",
                    key="signup_username",
                    help="3–32 letters, numbers, periods, underscores, or hyphens.",
                )
                password = st.text_input(
                    "Password",
                    type="password",
                    key="signup_pw",
                    help="At least 6 characters.",
                )
                submitted = st.form_submit_button("Create account", use_container_width=True)
            if submitted:
                result = supabase_client.sign_up_with_password(username, password)
                if "error" in result:
                    st.session_state.auth_error = result["error"]
                else:
                    st.session_state.access_token  = result["access_token"]
                    st.session_state.refresh_token = result["refresh_token"]
                    st.session_state.user_id       = result["user_id"]
                    st.session_state.username      = result["username"]
                st.rerun()

# Main content area - render based on current view
if st.session_state.current_view == 'landing':
    # Import and render landing page
    from frontend.views import landing
    landing.render()

elif st.session_state.current_view == 'scorer':
    # Import and render scorer page
    from frontend.views import scorer
    scorer.render()

elif st.session_state.current_view == 'history':
    # Import and render history page
    from frontend.views import history
    history.render()

elif st.session_state.current_view == 'resources':
    # Import and render resources page
    from frontend.views import resources
    resources.render()
