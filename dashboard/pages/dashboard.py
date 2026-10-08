import pandas as pd
import streamlit as st

from utils import get_incidents


st.title("Smart City Command Center")

st.caption(
    "Live overview of reported infrastructure incidents"
)


@st.fragment(run_every="5s")
def live_dashboard():

    try:
        incidents = get_incidents()

    except Exception as exc:
        st.error(
            f"API unavailable: {exc}"
        )
        return


    if not incidents:
        st.info("No incidents reported.")
        return


    df = pd.DataFrame(incidents)


    # -----------------------
    # KPI
    # -----------------------

    total = len(df)

    critical = len(
        df[df["severity"] == "CRITICAL"]
    )

    active = len(
        df[
            df["status"].isin(
                [
                    "REPORTED",
                    "VALIDATED",
                    "ASSIGNED",
                    "IN_PROGRESS"
                ]
            )
        ]
    )

    resolved = len(
        df[
            df["status"].isin(
                [
                    "RESOLVED",
                    "CLOSED"
                ]
            )
        ]
    )


    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Total incidents",
        total
    )

    col2.metric(
        "Active",
        active
    )

    col3.metric(
        "Critical",
        critical
    )

    col4.metric(
        "Resolved",
        resolved
    )


    st.divider()


    # -----------------------
    # MAP
    # -----------------------

    st.subheader("Incident Map")

    map_data = df.dropna(
        subset=[
            "latitude",
            "longitude"
        ]
    )


    if not map_data.empty:

        st.map(
            map_data,
            latitude="latitude",
            longitude="longitude",
            size=40
        )

    else:
        st.info(
            "No incidents with coordinates available."
        )


    st.divider()


    # -----------------------
    # CHARTS
    # -----------------------

    left, right = st.columns(2)


    with left:

        st.subheader(
            "Incidents by type"
        )

        category_counts = (
            df["category"]
            .value_counts()
            .rename_axis("category")
            .reset_index(name="count")
        )

        st.bar_chart(
            category_counts,
            x="category",
            y="count"
        )


    with right:

        st.subheader(
            "Incidents by status"
        )

        status_counts = (
            df["status"]
            .value_counts()
            .rename_axis("status")
            .reset_index(name="count")
        )

        st.bar_chart(
            status_counts,
            x="status",
            y="count"
        )


    st.divider()


    # -----------------------
    # TABLE
    # -----------------------

    st.subheader(
        "All Incidents"
    )


    display_columns = [
        "id",
        "name",
        "category",
        "severity",
        "status",
        "location",
        "department"
    ]


    st.dataframe(
        df[display_columns],
        hide_index=True
    )


live_dashboard()
