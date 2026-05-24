"""Checkpoint persistence using SQLite for the investment journey agent."""

import logging
from contextlib import AbstractContextManager
from langgraph.checkpoint.sqlite import SqliteSaver

logger = logging.getLogger(__name__)


def get_checkpointer(db_path: str = "checkpoints.sqlite") -> AbstractContextManager[SqliteSaver]:
    """
    Get SQLite checkpointer for state persistence.
    
    This allows the conversation to resume from where it stopped
    even after closing the terminal.
    
    Args:
        db_path: Path to the SQLite database file
        
    Returns:
        Context manager that yields a SqliteSaver instance configured for the database
    """
    logger.info(f"Inicializando checkpointer SQLite: {db_path}")
    
    return SqliteSaver.from_conn_string(db_path)


def get_thread_id(user_id: str) -> str:
    """
    Get thread ID for a user.
    
    The thread ID is used to identify a conversation thread in the checkpointer.
    For this simple CLI, we use the user_id directly as the thread_id.
    
    Args:
        user_id: User identifier
        
    Returns:
        Thread ID for checkpointing
    """
    return f"journey_agent_{user_id}"
