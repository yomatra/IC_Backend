import streamlit as st


st.set_page_config(
    page_title="Smart City Command Center",
    page_icon="🏙️",
    layout="wide"
)


dashboard_page = st.Page(
    "pages/dashboard.py",
    title="Dashboard",
    icon="📊",
    default=True
)

tickets_page = st.Page(
    "pages/tickets.py",
    title="Tickets",
    icon="🎫"
)


navigation = st.navigation(
    [
        dashboard_page,
        tickets_page
    ],
    position="top"
)


navigation.run()
