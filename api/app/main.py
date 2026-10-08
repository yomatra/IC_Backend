import os

from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any, Literal

import psycopg

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb


DATABASE_URL = os.environ["DATABASE_URL"]


# --------------------------------------------------
# DATABASE INITIALIZATION
# --------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):

    with psycopg.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:

            cur.execute(
                """
                CREATE SEQUENCE IF NOT EXISTS incident_number_seq
                START WITH 1
                INCREMENT BY 1;
                """
            )

    yield


# --------------------------------------------------
# APP
# --------------------------------------------------

app = FastAPI(
    title="Smart City Incident API",
    version="1.0.0",
    lifespan=lifespan
)


# --------------------------------------------------
# MODELS
# --------------------------------------------------

class StatusUpdate(BaseModel):
    status: Literal[
        "REPORTED",
        "VALIDATED",
        "ASSIGNED",
        "IN_PROGRESS",
        "RESOLVED",
        "CLOSED",
        "REJECTED"
    ]


ACTION_STATUS = {
    "REPORTED": "PotentialActionStatus",
    "VALIDATED": "PotentialActionStatus",
    "ASSIGNED": "PotentialActionStatus",
    "IN_PROGRESS": "ActiveActionStatus",
    "RESOLVED": "CompletedActionStatus",
    "CLOSED": "CompletedActionStatus",
    "REJECTED": "FailedActionStatus"
}


# --------------------------------------------------
# ROOT
# --------------------------------------------------

@app.get("/")
def root():

    return {
        "message": "Smart City API is running"
    }


# --------------------------------------------------
# HEALTH CHECK
# --------------------------------------------------

@app.get("/health")
def health():

    try:

        with psycopg.connect(DATABASE_URL) as conn:
            with conn.cursor() as cur:

                cur.execute("SELECT 1")
                cur.fetchone()

    except Exception as exc:

        raise HTTPException(
            status_code=503,
            detail="Database unavailable"
        ) from exc

    return {
        "status": "ok",
        "database": "ok"
    }


# --------------------------------------------------
# CREATE INCIDENT
# --------------------------------------------------

@app.post("/api/incidents", status_code=201)
def create_incident(data: dict[str, Any]):

    required_fields = [
        "name",
        "description",
        "dateCreated",
        "creativeWorkStatus",
        "city:severity",
        "city:category"
    ]

    missing_fields = [
        field
        for field in required_fields
        if field not in data
        or data[field] is None
        or data[field] == ""
    ]

    if missing_fields:

        raise HTTPException(
            status_code=422,
            detail={
                "error": "Missing required fields",
                "fields": missing_fields
            }
        )


    location = data.get(
        "spatialCoverage",
        {}
    )

    geo = location.get(
        "geo",
        {}
    ) or {}

    department = (
        data
        .get("potentialAction", {})
        .get("agent", {})
        .get("name")
    )


    with psycopg.connect(DATABASE_URL) as conn:

        with conn.cursor() as cur:

            # --------------------------------------
            # Generate unique server-side ID
            # --------------------------------------

            cur.execute(
                """
                SELECT nextval(
                    'incident_number_seq'
                )
                """
            )

            number = cur.fetchone()[0]

            year = datetime.now(
                timezone.utc
            ).year

            incident_id = (
                f"INC-{year}-{number:06d}"
            )


            # --------------------------------------
            # Override client IDs
            # --------------------------------------

            data["@id"] = (
                f"urn:incident:{incident_id}"
            )

            data["identifier"] = incident_id

            data["reportNumber"] = incident_id


            # --------------------------------------
            # INSERT
            # --------------------------------------

            cur.execute(
                """
                INSERT INTO incidents (
                    id,
                    name,
                    description,
                    category,
                    severity,
                    status,
                    location,
                    latitude,
                    longitude,
                    department,
                    created_at,
                    updated_at,
                    raw_json
                )

                VALUES (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s
                )
                """,

                (
                    incident_id,

                    data["name"],

                    data["description"],

                    data["city:category"],

                    data["city:severity"],

                    data["creativeWorkStatus"],

                    location.get("name"),

                    geo.get("latitude"),

                    geo.get("longitude"),

                    department,

                    data["dateCreated"],

                    data.get(
                        "dateModified",
                        data["dateCreated"]
                    ),

                    Jsonb(data)
                )
            )


    return {
        "status": "stored",
        "incident": incident_id
    }


# --------------------------------------------------
# GET ALL INCIDENTS
# --------------------------------------------------

@app.get("/api/incidents")
def get_incidents():

    with psycopg.connect(
        DATABASE_URL,
        row_factory=dict_row
    ) as conn:

        with conn.cursor() as cur:

            cur.execute(
                """
                SELECT
                    id,
                    name,
                    description,
                    category,
                    severity,
                    status,
                    location,
                    latitude,
                    longitude,
                    department,
                    created_at,
                    updated_at

                FROM incidents

                ORDER BY created_at DESC
                """
            )

            return cur.fetchall()


# --------------------------------------------------
# GET SINGLE INCIDENT
# --------------------------------------------------

@app.get("/api/incidents/{incident_id}")
def get_incident(
    incident_id: str
):

    with psycopg.connect(
        DATABASE_URL,
        row_factory=dict_row
    ) as conn:

        with conn.cursor() as cur:

            cur.execute(
                """
                SELECT
                    id,
                    name,
                    description,
                    category,
                    severity,
                    status,
                    location,
                    latitude,
                    longitude,
                    department,
                    created_at,
                    updated_at,
                    raw_json

                FROM incidents

                WHERE id = %s
                """,
                (
                    incident_id,
                )
            )

            incident = cur.fetchone()


    if incident is None:

        raise HTTPException(
            status_code=404,
            detail="Incident not found"
        )


    return incident


# --------------------------------------------------
# UPDATE STATUS
# --------------------------------------------------

@app.patch(
    "/api/incidents/{incident_id}/status"
)
def update_incident_status(
    incident_id: str,
    update: StatusUpdate
):

    with psycopg.connect(
        DATABASE_URL,
        row_factory=dict_row
    ) as conn:

        with conn.cursor() as cur:

            # --------------------------------------
            # Load JSON-LD
            # --------------------------------------

            cur.execute(
                """
                SELECT raw_json

                FROM incidents

                WHERE id = %s
                """,
                (
                    incident_id,
                )
            )

            result = cur.fetchone()


            if result is None:

                raise HTTPException(
                    status_code=404,
                    detail="Incident not found"
                )


            raw_json = result["raw_json"]


            # --------------------------------------
            # Update timestamp
            # --------------------------------------

            now = datetime.now(
                timezone.utc
            ).isoformat()


            # --------------------------------------
            # Update JSON-LD
            # --------------------------------------

            raw_json[
                "creativeWorkStatus"
            ] = update.status

            raw_json[
                "dateModified"
            ] = now


            if (
                "potentialAction"
                in raw_json
                and isinstance(
                    raw_json["potentialAction"],
                    dict
                )
            ):

                raw_json[
                    "potentialAction"
                ][
                    "actionStatus"
                ] = ACTION_STATUS[
                    update.status
                ]


            # --------------------------------------
            # Update DB
            # --------------------------------------

            cur.execute(
                """
                UPDATE incidents

                SET
                    status = %s,
                    updated_at = %s,
                    raw_json = %s

                WHERE id = %s
                """,

                (
                    update.status,
                    now,
                    Jsonb(raw_json),
                    incident_id
                )
            )


    return {
        "status": "updated",
        "incident": incident_id,
        "new_status": update.status
    }
