"""Helpers for publishing queue state into Firestore."""

from typing import Any, cast

from fastapi import BackgroundTasks

from app.db.models.queue import Queue
from app.firebase.firestore import update_queue_state


def _queue_type_value(queue: Queue) -> str:
    queue_type = cast(Any, queue.queue_type)
    value = queue_type.value if hasattr(queue_type, "value") else queue_type
    return str(value).lower()


def enqueue_queue_state_sync(background_tasks: BackgroundTasks, queue: Queue) -> None:
    """Publish a queue document asynchronously after an API mutation."""
    background_tasks.add_task(sync_queue_state, queue)


def sync_queue_state(queue: Queue) -> None:
    """Write a queue document to Firestore using the attendee-facing shape."""
    update_queue_state(
        str(queue.venue_id),
        str(queue.id),
        cast(int, queue.estimated_wait_minutes),
        cast(bool, queue.is_open),
        cast(int, queue.current_length),
        annotation=cast(str | None, queue.annotation),
        name=cast(str | None, queue.name),
        zone_id=str(queue.zone_id) if cast(object | None, queue.zone_id) else None,
        queue_type=_queue_type_value(queue),
        throughput_per_minute=cast(float | None, queue.throughput_per_minute),
    )
