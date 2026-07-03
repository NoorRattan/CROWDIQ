"""Google Maps helpers wrapped for async FastAPI usage."""

import asyncio
import logging
import re
from typing import Any

import googlemaps
from fastapi import HTTPException, status
from googlemaps.exceptions import ApiError, Timeout, TransportError

from app.core.config import settings
from app.schemas.venue import RouteResponse, RouteStep

logger = logging.getLogger(__name__)

_gmaps: googlemaps.Client | None = None


def _get_client() -> googlemaps.Client:
    global _gmaps
    if _gmaps is None:
        if not settings.GOOGLE_MAPS_API_KEY:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Google Maps API key is not configured.",
            )
        try:
            _gmaps = googlemaps.Client(key=settings.GOOGLE_MAPS_API_KEY, timeout=10)
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Google Maps API key is invalid.",
            ) from exc
    return _gmaps


async def calculate_route(
    origin_lat: float,
    origin_lng: float,
    dest_lat: float,
    dest_lng: float,
) -> RouteResponse:
    """Calculate a walking route using the synchronous Google Maps client."""
    loop = asyncio.get_running_loop()
    try:
        directions = await loop.run_in_executor(
            None,
            lambda: _get_client().directions(
                origin=(origin_lat, origin_lng),
                destination=(dest_lat, dest_lng),
                mode="walking",
                units="metric",
            ),
        )
    except (ApiError, Timeout, TransportError) as exc:
        logger.error("Google Maps directions call failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Navigation service is temporarily unavailable.",
        ) from exc

    if not directions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No walking route found.",
        )

    leg = directions[0]["legs"][0]
    return RouteResponse(
        distance=leg["distance"]["text"],
        duration=leg["duration"]["text"],
        steps=[
            RouteStep(
                instruction=_strip_html(step["html_instructions"]),
                distance=step["distance"]["text"],
                duration=step["duration"]["text"],
                start_lat=step["start_location"]["lat"],
                start_lng=step["start_location"]["lng"],
            )
            for step in leg["steps"]
        ],
        polyline=directions[0]["overview_polyline"]["points"],
    )


async def calculate_evacuation_routes(
    venue_zones: list[dict[str, Any]],
    safe_exits: list[dict[str, Any]],
) -> dict[str, Any]:
    """Calculate evacuation routes for each zone to the closest safe exit."""
    if not safe_exits:
        return {}

    routes: dict[str, Any] = {}
    for zone in venue_zones:
        nearest_exit = _find_nearest_exit(zone, safe_exits)
        if nearest_exit is None:
            continue
        try:
            route = await calculate_route(
                zone["lat_center"],
                zone["lng_center"],
                nearest_exit["lat"],
                nearest_exit["lng"],
            )
            routes[zone["id"]] = {
                "exit_name": nearest_exit["name"],
                "distance": route.distance,
                "duration": route.duration,
                "steps": [step.model_dump() for step in route.steps],
                "polyline": route.polyline,
            }
        except HTTPException:
            continue
    return routes


def _find_nearest_exit(
    zone: dict[str, Any],
    exits: list[dict[str, Any]],
) -> dict[str, Any] | None:
    """Return the closest safe exit for a zone or `None`."""
    if not exits:
        return None
    return min(
        exits,
        key=lambda exit_zone: (
            (exit_zone["lat"] - zone["lat_center"]) ** 2
            + (exit_zone["lng"] - zone["lng_center"]) ** 2
        ),
    )


def _strip_html(value: str) -> str:
    """Strip HTML tags from Google Maps instructions."""
    return re.sub(r"<[^>]+>", "", value).strip()
