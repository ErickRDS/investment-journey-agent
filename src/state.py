"""State management for the investment journey agent using TypedDict."""

from typing import TypedDict, Optional, List, Dict


class JourneyState(TypedDict):
    """
    Typed state for the investment journey.
    
    This state is passed through all LangGraph nodes and persisted via checkpointing.
    """
    # User identification
    user_id: str
    
    # Journey navigation
    current_step: str
    previous_step: Optional[str]
    
    # User inputs
    user_input: Optional[str]
    
    # Collected user data
    user_name: Optional[str]
    investment_goal: Optional[str]
    risk_profile: Optional[str]
    time_horizon: Optional[str]
    
    # Journey metadata
    last_message: Optional[str]
    llm_explanation: Optional[str]
    history: List[Dict[str, str]]
    error_count: int
    should_exit: bool


def create_initial_state(user_id: str = "default_user") -> JourneyState:
    """
    Create the initial state for a new journey.
    
    Args:
        user_id: Unique identifier for the user
        
    Returns:
        Initial JourneyState with default values
    """
    return JourneyState(
        user_id=user_id,
        current_step="start",
        previous_step=None,
        user_input=None,
        user_name=None,
        investment_goal=None,
        risk_profile=None,
        time_horizon=None,
        last_message=None,
        llm_explanation=None,
        history=[],
        error_count=0,
        should_exit=False,
    )


def validate_state(state: JourneyState) -> bool:
    """
    Validate that the state has all required fields.
    
    Args:
        state: The state to validate
        
    Returns:
        True if valid, False otherwise
    """
    required_fields = ["user_id", "current_step", "history", "error_count", "should_exit"]
    return all(field in state for field in required_fields)
