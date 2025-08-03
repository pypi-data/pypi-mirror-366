"""Streamlit session initializer"""

import streamlit as st


def initilizer_payslip_parser():
    """Session state variables initializer for payslip parser"""
    if 'payslip_pdf' not in st.session_state:
        st.session_state.payslip_pdf = None
    if 'parsed_payslips' not in st.session_state:
        st.session_state.parsed_payslips = None
    if 'all_payslips' not in st.session_state:
        st.session_state.all_payslips = None
    if 'monthyrs_dict' not in st.session_state:
        st.session_state.monthyrs_dict = None
    if 'agg_paycomps' not in st.session_state:
        st.session_state.agg_paycomps = None
    if 'action_button' not in st.session_state:
        st.session_state.action_button = None
    if 'display_res' not in st.session_state:
        st.session_state.display_res = None


def initialize_file_manager():
    """Session state variables initializer for movies manager"""
    st.session_state.setdefault('log_lines', [])
    st.session_state.setdefault('elapsed_tstr', "")
    st.session_state.setdefault('summary_text', "")
    st.session_state.setdefault('submit_button', False)
    st.session_state.setdefault('just_finished', False)
    st.session_state.setdefault('summary_data', None)
    st.session_state.setdefault('edited_data', None)
    st.session_state.setdefault('consol_summary', None)
