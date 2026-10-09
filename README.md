# IC_Backend – Smart City Incident Management

Backend and dashboard for the **Smart City Incident Reporting** prototype developed for the Innovation Challenge.

The system receives structured JSON-LD incident reports, stores them in PostgreSQL and provides a web-based dashboard for monitoring and managing incidents.

## Architecture

```text
Halerium / AI Assistant
        │
        │ JSON-LD
        ▼
     FastAPI
        │
        ▼
   PostgreSQL
        │
        ▼
Streamlit Dashboard
```

## Features

- FastAPI REST API
- PostgreSQL incident storage
- Server-generated incident IDs
- JSON-LD / schema.org based reports
- Incident overview dashboard
- Ticket management
- Status updates
- Severity classification
- Location and map visualization
- Docker-based environment
- Cloudflare Tunnel support

## Project Structure

```text
IC_Backend/
├── api/          # FastAPI backend
├── dashboard/    # Streamlit dashboard
├── db/           # PostgreSQL initialization
├── compose.yaml
└── smart-city-start.sh
```

## Start

Requirements:

- Docker + Docker Compose
- cloudflared
- Alacritty (for the included start script)

Start everything with:

```bash
./smart-city-start.sh
```

Or manually:

```bash
docker compose up --build
```

Local services:

```text
API:       http://localhost:8000
API Docs:  http://localhost:8000/docs
Dashboard: http://localhost:8501
```

## API

Main endpoints:

```text
POST   /api/incidents
GET    /api/incidents
GET    /api/incidents/{id}
PATCH  /api/incidents/{id}/status
GET    /health
```

## Tech Stack

- Python
- FastAPI
- PostgreSQL
- Streamlit
- Docker
- Cloudflare Tunnel
- JSON-LD / schema.org
