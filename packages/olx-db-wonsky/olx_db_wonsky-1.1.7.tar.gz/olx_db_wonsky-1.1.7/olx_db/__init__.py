"""
OLX Database package for managing OLX monitoring tasks and item records.
"""

from .version import __version__

# Import key components for easier access
from .db import (
    Base,
    MonitoringTask,
    ItemRecord,
    get_db,
    init_db,
    get_tasks_by_chat_id,
    get_task_by_chat_and_name,
    get_task_by_chat_id,
    create_task,
    delete_task_by_chat_id,
    get_all_tasks,
    get_pending_tasks,
    update_last_got_item,
    get_items_to_send_for_task,
    now_warsaw,
    delete_items_older_than_n_days
)

from .config import settings

# Export all important components
__all__ = [
    "Base",
    "MonitoringTask",
    "ItemRecord",
    "get_db",
    "init_db",
    "get_tasks_by_chat_id",
    "get_task_by_chat_and_name",
    "get_task_by_chat_id",
    "create_task",
    "delete_task_by_chat_id",
    "get_all_tasks",
    "get_pending_tasks",
    "update_last_got_item",
    "get_items_to_send_for_task",
    "now_warsaw",
    "settings",
    "delete_items_older_than_n_days"
]
