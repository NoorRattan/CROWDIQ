# CrowdIQ

CrowdIQ is a smart stadium experience platform built for the Physical Event Experience vertical. It combines a React attendee app, an admin dashboard, and a FastAPI backend to surface live crowd density, queue pressure, navigation, emergency routing, and venue operations data in one system.

## Chosen Vertical

Physical Event Experience.

The project focuses on large venues such as stadiums and arenas where crowd buildup, queue delays, navigation confusion, and emergency coordination all create operational risk and a poor attendee experience.

## Approach and Logic

The solution is designed around one core idea: venue decisions should be driven by live operational state instead of static signage or delayed manual updates.

Key design choices:

- Firestore real-time listeners push live updates to clients without polling.
- Google Maps is used as the primary visual surface for crowd zones, routing, and evacuation overlays.
- Zustand keeps the frontend state lightweight and predictable for fast attendee interactions.
- FastAPI exposes backend APIs for crowd updates, routing, analytics, orders, and emergency workflows.
- ML helpers are used for congestion prediction and wait-time forecasting so the system can react before a bottleneck becomes critical.

## How the Solution Works

1. Venue data, crowd density, queue state, and emergency status are stored and updated through the backend and Firebase.
2. Attendee clients subscribe to live venue state and render crowd heatmaps, queue updates, and navigation guidance in real time.
3. Admin users can monitor live venue conditions, trigger emergency actions, and manage operational views through the dashboard.
4. When navigation is requested, the app renders route overlays on the venue map.
5. When emergency mode is activated, the interface switches to evacuation guidance and route visualization.

Main capabilities:

- Live crowd heatmap by venue zone
- Queue monitoring and congestion visibility
- Attendee navigation across the venue
- Emergency evacuation route guidance
- Admin analytics and operational monitoring
- Seat, order, and staff management views

## Repository Structure

```text
backend/   FastAPI application, APIs, services, ML helpers, tests
frontend/  React + Vite application for attendee and admin flows
```

## Live Demo

| Surface | URL |
|---------|-----|
| Attendee PWA | https://promptwar-db092.web.app |
| Admin Dashboard | https://promptwar-db092.web.app/admin |
| API Documentation | https://crowdiq-api-667912434114.us-central1.run.app/docs |
| Demo Mode (guest) | https://promptwar-db092.web.app?demo=true |

**Demo credentials:**

| Role | Email | Password |
|------|-------|----------|
| Attendee | demo@crowdiq.app | Demo1234! |
| Admin | admin@crowdiq.app | Admin1234! |
| Guest | Click "Continue as Guest" | — |

## Running the Project

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8080
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Environment values should be supplied through `backend/.env` and `frontend/.env.local`. Start from `backend/.env.example` and `frontend/.env.example`; never commit real Firebase or Google API keys.

## Assumptions Made

- Crowd density values are provided by staff updates or external sensors; the project does not include physical sensing hardware.
- Venue maps and floor-plan overlays depend on valid venue coordinates and uploaded floor-plan assets.
- Payment processing is out of scope; ordering flows focus on operational state rather than checkout integration.
- The ML components use demo or synthetic patterns suitable for a prototype, not production-trained venue data.
- Firebase and Google Maps credentials are available in the deployment environment.

## Submission Notes

- Public repository target: GitHub
- Primary branch for submission: `main`
- README includes the required sections: chosen vertical, approach and logic, how the solution works, and assumptions made
