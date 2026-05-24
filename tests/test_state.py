"""Tests for state management."""

import pytest
from src.state import create_initial_state, validate_state, JourneyState


def test_create_initial_state():
    """Test that initial state is created correctly."""
    state = create_initial_state("test_user")
    
    assert state["user_id"] == "test_user"
    assert state["current_step"] == "start"
    assert state["previous_step"] is None
    assert state["user_input"] is None
    assert state["user_name"] is None
    assert state["investment_goal"] is None
    assert state["risk_profile"] is None
    assert state["time_horizon"] is None
    assert state["last_message"] is None
    assert state["llm_explanation"] is None
    assert state["history"] == []
    assert state["error_count"] == 0
    assert state["should_exit"] is False


def test_validate_state_valid():
    """Test that valid state passes validation."""
    state = create_initial_state("test_user")
    assert validate_state(state) is True


def test_validate_state_missing_field():
    """Test that state with missing required field fails validation."""
    # Create incomplete state
    incomplete_state: JourneyState = {
        "user_id": "test_user",
        "current_step": "start",
        "previous_step": None,
        "user_input": None,
        "user_name": None,
        "investment_goal": None,
        "risk_profile": None,
        "time_horizon": None,
        "last_message": None,
        "llm_explanation": None,
        # Missing history, error_count, should_exit
    }
    
    # This should fail validation
    assert validate_state(incomplete_state) is False


def test_state_stores_user_answers():
    """Test that user answers are stored in state."""
    state = create_initial_state("test_user")
    
    # Simulate collecting user data
    state["user_name"] = "João"
    state["investment_goal"] = "Aposentadoria"
    state["risk_profile"] = "Moderado"
    state["time_horizon"] = "Mais de 5 anos"
    
    # Verify data is stored
    assert state["user_name"] == "João"
    assert state["investment_goal"] == "Aposentadoria"
    assert state["risk_profile"] == "Moderado"
    assert state["time_horizon"] == "Mais de 5 anos"


def test_state_tracks_journey_progress():
    """Test that state tracks journey progress through steps."""
    state = create_initial_state("test_user")
    
    # Simulate journey progression
    state["current_step"] = "ask_name"
    state["previous_step"] = "start"
    assert state["current_step"] == "ask_name"
    assert state["previous_step"] == "start"
    
    state["current_step"] = "ask_goal"
    state["previous_step"] = "ask_name"
    assert state["current_step"] == "ask_goal"
    assert state["previous_step"] == "ask_name"


def test_state_history_accumulates():
    """Test that history accumulates messages."""
    state = create_initial_state("test_user")
    
    # Add messages to history
    state["history"].append({"step": "start", "message": "Welcome"})
    state["history"].append({"step": "ask_name", "message": "What's your name?"})
    
    assert len(state["history"]) == 2
    assert state["history"][0]["step"] == "start"
    assert state["history"][1]["step"] == "ask_name"


def test_state_error_count_increments():
    """Test that error count can be incremented."""
    state = create_initial_state("test_user")
    
    assert state["error_count"] == 0
    
    state["error_count"] += 1
    assert state["error_count"] == 1
    
    state["error_count"] += 1
    assert state["error_count"] == 2


def test_state_exit_flag():
    """Test that exit flag can be set."""
    state = create_initial_state("test_user")
    
    assert state["should_exit"] is False
    
    state["should_exit"] = True
    assert state["should_exit"] is True
