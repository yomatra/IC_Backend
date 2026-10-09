import streamlit as st

from utils import (
    get_incident,
    get_incidents,
    update_status
)


STATUSES = [
    "REPORTED",
    "VALIDATED",
    "ASSIGNED",
    "IN_PROGRESS",
    "RESOLVED",
    "CLOSED",
    "REJECTED"
]


SEVERITY_ICONS = {
    "LOW": "🟢",
    "MEDIUM": "🟡",
    "HIGH": "🟠",
    "CRITICAL": "🔴"
}


st.title("Incident Tickets")

st.caption(
    "Review and manage individual incidents"
)


# --------------------------------------------------
# LOAD INCIDENTS
# --------------------------------------------------

try:
    incidents = get_incidents()

except Exception as exc:
    st.error(
        f"API unavailable: {exc}"
    )
    st.stop()


if not incidents:
    st.info(
        "No tickets available."
    )
    st.stop()


# --------------------------------------------------
# INCIDENT MAP
# --------------------------------------------------

incident_map = {
    incident["id"]: incident
    for incident in incidents
}


def format_ticket(incident_id):

    incident = incident_map[incident_id]

    severity = incident.get(
        "severity",
        "UNKNOWN"
    )

    icon = SEVERITY_ICONS.get(
        severity,
        "⚪"
    )

    return (
        f"{icon} "
        f"{incident_id} — "
        f"{incident['name']} — "
        f"{severity}"
    )


# --------------------------------------------------
# SELECT TICKET
# --------------------------------------------------

selected_id = st.selectbox(
    "Select ticket",
    options=list(incident_map.keys()),
    format_func=format_ticket
)


# --------------------------------------------------
# LOAD SINGLE TICKET
# --------------------------------------------------

try:
    ticket = get_incident(
        selected_id
    )

except Exception as exc:
    st.error(
        f"Could not load ticket: {exc}"
    )
    st.stop()


st.divider()


# --------------------------------------------------
# HEADER
# --------------------------------------------------

st.subheader(
    ticket["name"]
)

st.caption(
    ticket["id"]
)


severity = ticket["severity"]

severity_display = {
    "LOW": "🟢 LOW",
    "MEDIUM": "🟡 MEDIUM",
    "HIGH": "🟠 HIGH",
    "CRITICAL": "🔴 CRITICAL"
}.get(
    severity,
    "⚪ UNKNOWN"
)


col1, col2, col3 = st.columns(3)


col1.metric(
    "Severity",
    severity_display
)

col2.metric(
    "Status",
    ticket["status"]
)

col3.metric(
    "Category",
    ticket["category"]
)


st.divider()


# --------------------------------------------------
# DETAILS
# --------------------------------------------------

left, right = st.columns(2)


with left:

    st.subheader("Incident")

    st.write(
        "**Description**"
    )

    st.write(
        ticket["description"]
    )

    st.write(
        "**Location**"
    )

    st.write(
        ticket["location"]
        or "Unknown"
    )


with right:

    st.subheader("Assignment")

    st.write(
        "**Department**"
    )

    st.write(
        ticket["department"]
        or "Unassigned"
    )

    st.write(
        "**Created**"
    )

    st.write(
        ticket["created_at"]
    )


st.divider()


# --------------------------------------------------
# STATUS UPDATE
# --------------------------------------------------

st.subheader(
    "Update Status"
)


current_status = ticket["status"]

current_index = (
    STATUSES.index(current_status)
    if current_status in STATUSES
    else 0
)


new_status = st.selectbox(
    "Status",
    STATUSES,
    index=current_index
)


if st.button(
    "Update ticket",
    type="primary"
):

    try:

        update_status(
            selected_id,
            new_status
        )

        st.success(
            f"Status changed to {new_status}"
        )

        st.rerun()

    except Exception as exc:

        st.error(
            f"Update failed: {exc}"
        )


st.divider()


# --------------------------------------------------
# RAW JSON
# --------------------------------------------------

with st.expander(
    "Show JSON-LD report"
):

    st.json(
        ticket["raw_json"]
    )
