"""Helpers for publishing queue state into Firestore."""

from fastapi import BackgroundTasks

from app.db.models.queue import Queue
from app.firebase.firestore import update_queue_state


def _queue_type_value(queue: Queue) -> str:
    queue_type = (
        queue.queue_type.value
        if hasattr(queue.queue_type, "value")
        else str(queue.queue_type)
    )
    return queue_type.lower()


def enqueue_queue_state_sync(background_tasks: BackgroundTasks, queue: Queue) -> None:
    """Publish a queue document asynchronously after an API mutation."""
    background_tasks.add_task(sync_queue_state, queue)


def sync_queue_state(queue: Queue) -> None:
    """Write a queue document to Firestore using the attendee-facing shape."""
    update_queue_state(
        str(queue.venue_id),
        str(queue.id),
        queue.estimated_wait_minutes,
        queue.is_open,
        queue.current_length,
        annotation=queue.annotation,
        name=queue.name,
        zone_id=str(queue.zone_id) if queue.zone_id else None,
        queue_type=_queue_type_value(queue),
        throughput_per_minute=queue.throughput_per_minute,
    )
