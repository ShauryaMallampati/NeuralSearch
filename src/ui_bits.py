"""
Reusable UI components for the Streamlit app
keeps the pages clean and consistent
"""

import streamlit as st


def page_header(title: str, subtitle: str = None, emoji: str = None):
    """render a consistent page header"""
    if emoji:
        st.title(f"{emoji} {title}")
    else:
        st.title(title)
    
    if subtitle:
        st.caption(subtitle)
    
    st.divider()


def info_box(message: str, icon: str = ""):
    """friendly info message"""
    st.info(f"{icon} {message}")


def warning_box(message: str, icon: str = ""):
    """warning message for caution-needed situations"""
    st.warning(f"{icon} {message}")


def error_box(message: str, icon: str = ""):
    """error message"""
    st.error(f"{icon} {message}")


def success_box(message: str, icon: str = ""):
    """success message"""
    st.success(f"{icon} {message}")


def metric_row(metrics: list[tuple[str, str, str]]):
    """
    display a row of metrics
    
    Args:
        metrics: List of (label, value, help_text) tuples
    """
    cols = st.columns(len(metrics))
    for col, (label, value, help_text) in zip(cols, metrics):
        with col:
            st.metric(label=label, value=value, help=help_text)


def no_index_warning():
    """standard warning when index doesn't exist"""
    st.warning(
        "No search index found!\n\n"
        "Head over to the **Upload & Index** page to:\n"
        "1. Upload some PDFs\n"
        "2. Build the search index\n\n"
        "Then come back here to search!"
    )


def empty_state(message: str, icon: str = ""):
    """display an empty state with a friendly message"""
    st.markdown(
        f"""
        <div style="text-align: center; padding: 2rem; color: #666;">
            <p style="font-size: 3rem; margin-bottom: 0.5rem;">{icon}</p>
            <p>{message}</p>
        </div>
        """,
        unsafe_allow_html=True
    )


def confirm_action(key: str, message: str = "Are you sure?") -> bool:
    """
    simple confirmation pattern using session state
    returns True if user confirmed
    """
    confirm_key = f"confirm_{key}"
    
    if confirm_key not in st.session_state:
        st.session_state[confirm_key] = False
    
    if st.session_state[confirm_key]:
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Yes, do it", key=f"{key}_yes"):
                st.session_state[confirm_key] = False
                return True
        with col2:
            if st.button("Cancel", key=f"{key}_no"):
                st.session_state[confirm_key] = False
        st.caption(message)
        return False
    
    return False


def set_confirm(key: str):
    """set confirmation state to True"""
    st.session_state[f"confirm_{key}"] = True
