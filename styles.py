import streamlit as st


@st.cache_data(show_spinner=False)
def _workspace_css() -> str:
    return """
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    :root {
        --bg-main: #FAFBFC;
        --bg-card: #FFFFFF;
        --bg-sidebar: #1A1C2E;
        --text-main: #1F2937;
        --text-muted: #6B7280;
        --accent: #007BFF;
        --border: #E5E7EB;
        --zebra: #F8FAFC;
    }

    html, body, [class*="css"] {
        font-family: 'Inter', 'Source Sans Pro', sans-serif !important;
    }

    .stApp {
        background: var(--bg-main);
        color: var(--text-main);
    }

    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
        padding-left: 2.25rem !important;
        padding-right: 2.25rem !important;
        max-width: 1200px;
    }

    [data-testid="stSidebar"] > div:first-child {
        background: var(--bg-sidebar) !important;
        padding-top: 1rem !important;
        padding-left: 0.65rem !important;
        padding-right: 0.65rem !important;
    }

    [data-testid="stSidebar"] {
        min-width: 235px !important;
        max-width: 235px !important;
    }

    [data-testid="stSidebar"] * {
        color: #E5E7EB !important;
    }

    [data-testid="stSidebar"] [role="radiogroup"] label {
        border-radius: 8px !important;
        padding: 0.35rem 0.5rem !important;
    }

    [data-testid="stSidebar"] [role="radiogroup"] label:hover {
        background: rgba(255, 255, 255, 0.08) !important;
    }

    [data-testid="metric-container"] {
        background: var(--bg-card) !important;
        border: 1px solid var(--border) !important;
        border-radius: 12px !important;
        box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.05) !important;
        padding: 0.9rem 1rem !important;
    }

    [data-testid="stMetricLabel"] {
        color: var(--text-muted) !important;
        font-weight: 600 !important;
    }

    [data-testid="stMetricValue"] {
        color: var(--text-main) !important;
        font-weight: 700 !important;
    }

    [data-testid="stMetricDelta"] {
        color: var(--accent) !important;
    }

    .stButton > button,
    [data-testid="baseButton-secondary"],
    [data-testid="baseButton-primary"] {
        background: var(--accent) !important;
        color: #FFFFFF !important;
        border: 1px solid var(--accent) !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
    }

    .stButton > button:hover,
    [data-testid="baseButton-secondary"]:hover,
    [data-testid="baseButton-primary"]:hover {
        filter: brightness(0.95);
    }

    .stDataFrame table,
    .stTable table {
        border-collapse: collapse !important;
        border: 1px solid var(--border) !important;
    }

    .stDataFrame thead tr th,
    .stTable thead tr th {
        background: #FFFFFF !important;
        border-bottom: 1px solid var(--border) !important;
        color: #374151 !important;
        font-weight: 600 !important;
    }

    .stDataFrame tbody tr:nth-child(even),
    .stTable tbody tr:nth-child(even) {
        background: var(--zebra) !important;
    }

    .stDataFrame tbody tr td,
    .stTable tbody tr td {
        border-bottom: 1px solid #F1F5F9 !important;
    }

    hr {
        border: none;
        border-top: 1px solid #EEF2F7;
    }
    """


def apply_workspace_theme() -> None:
    st.markdown(f"<style>{_workspace_css()}</style>", unsafe_allow_html=True)
