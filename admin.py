import streamlit as st
from config import SecureConfig

def admin_required():
    """Decorator to require admin authentication"""
    if not SecureConfig.is_development():
        st.error("Admin panel is not available in production")
        st.stop()
    
    if "admin_authenticated" not in st.session_state:
        st.session_state.admin_authenticated = False
    
    if not st.session_state.admin_authenticated:
        password = st.text_input("Admin Password", type="password")
        if st.button("Login"):
            if password == SecureConfig.get_admin_password():
                st.session_state.admin_authenticated = True
                st.rerun()
            else:
                st.error("Invalid password")
        st.stop()
