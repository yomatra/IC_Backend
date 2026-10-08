import os
import requests


API_URL = os.getenv(
    "API_BASE_URL",
    "http://localhost:8000"
)


def get_incidents():

    response = requests.get(
        f"{API_URL}/api/incidents",
        timeout=10
    )

    response.raise_for_status()

    return response.json()


def get_incident(incident_id):

    response = requests.get(
        f"{API_URL}/api/incidents/{incident_id}",
        timeout=10
    )

    response.raise_for_status()

    return response.json()


def update_status(
    incident_id,
    status
):

    response = requests.patch(
        f"{API_URL}/api/incidents/{incident_id}/status",
        json={
            "status": status
        },
        timeout=10
    )

    response.raise_for_status()

    return response.json()
