import streamlit as st

def render_alert_css():
    """Injects the CSS styles for the pulsing red banner."""
    st.markdown("""
        <style>
        .critical-alert {
            padding: 20px;
            background-color: #ff4b4b;
            color: white;
            border-radius: 10px;
            margin-bottom: 20px;
            font-weight: bold;
            text-align: center;
            font-size: 20px;
            animation: pulse 2s infinite;
            box-shadow: 0 4px 6px rgba(0,0,0,0.2);
            border: 2px solid #ff0000;
        }
        @keyframes pulse {
            0% { opacity: 1; transform: scale(1); }
            50% { opacity: 0.85; transform: scale(1.01); }
            100% { opacity: 1; transform: scale(1); }
        }
        </style>
    """, unsafe_allow_html=True)

def show_alert_banner(messages):
    """
    Takes a list of warning messages and renders them as critical banners.
    """
    if not messages:
        st.success("✅ System Nominal: No Active Disasters Detected")
        return

    # 1. Inject the CSS
    render_alert_css()

    # 2. Render each alert
    for msg in messages:
        st.markdown(f'<div class="critical-alert">⚠️ {msg}</div>', unsafe_allow_html=True)