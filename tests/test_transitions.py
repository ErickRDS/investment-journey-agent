"""Tests for journey transitions and graph routing."""

import pytest
from unittest.mock import Mock, patch
from src.state import create_initial_state
from src.agent import compile_journey_graph
from src.nodes import (
    start_node,
    ask_name_node,
    process_name_node,
    ask_goal_node,
    process_goal_node,
)


def test_start_node_transitions_to_ask_name():
    """Test that start node correctly transitions to ask_name."""
    state = create_initial_state("test_user")
    
    # Execute start node
    result = start_node(state)
    
    # Verify state updates
    assert result["current_step"] == "ask_name"
    assert result["previous_step"] == "start"
    assert result["last_message"] is not None
    assert len(result["history"]) == 1


def test_ask_name_node_shows_prompt():
    """Test that ask_name node shows the name prompt."""
    state = create_initial_state("test_user")
    state["current_step"] = "ask_name"
    
    # Execute ask_name node
    result = ask_name_node(state)
    
    # Verify prompt is shown
    assert result["last_message"] is not None
    assert "nome" in result["last_message"].lower()


def test_process_name_valid_input():
    """Test that valid name input advances to ask_goal."""
    state = create_initial_state("test_user")
    state["current_step"] = "ask_name"
    state["user_input"] = "João Silva"
    
    # Execute process_name node
    result = process_name_node(state)
    
    # Verify name is stored and step advances
    assert result["user_name"] == "João Silva"
    assert result["current_step"] == "ask_goal"
    assert result["error_count"] == 0


def test_process_name_invalid_input():
    """Test that invalid name input stays at ask_name."""
    state = create_initial_state("test_user")
    state["current_step"] = "ask_name"
    state["user_input"] = ""  # Empty input
    
    # Execute process_name node
    result = process_name_node(state)
    
    # Verify stays at ask_name and error count increases
    assert result["user_name"] is None
    assert result["current_step"] == "ask_name"
    assert result["error_count"] == 1


def test_process_name_rejects_numeric_only_input():
    """Test that numeric-only input is not accepted as a name."""
    state = create_initial_state("test_user")
    state["current_step"] = "ask_name"
    state["user_input"] = "928"
    
    result = process_name_node(state)
    
    assert result["user_name"] is None
    assert result["current_step"] == "ask_name"
    assert result["error_count"] == 1
    assert "nome" in result["last_message"].lower()


def test_process_goal_valid_option_number():
    """Test that valid goal option (number) advances to ask_risk_profile."""
    state = create_initial_state("test_user")
    state["current_step"] = "ask_goal"
    state["user_name"] = "João"
    state["user_input"] = "1"  # Reserva de emergência
    
    # Execute process_goal node
    result = process_goal_node(state)
    
    # Verify goal is stored and step advances
    assert result["investment_goal"] == "Reserva de emergência"
    assert result["current_step"] == "ask_risk_profile"
    assert result["error_count"] == 0


def test_process_goal_valid_option_text():
    """Test that valid goal option (text) advances to ask_risk_profile."""
    state = create_initial_state("test_user")
    state["current_step"] = "ask_goal"
    state["user_name"] = "João"
    state["user_input"] = "aposentadoria"  # Partial match
    
    # Execute process_goal node
    result = process_goal_node(state)
    
    # Verify goal is stored and step advances
    assert result["investment_goal"] == "Aposentadoria"
    assert result["current_step"] == "ask_risk_profile"
    assert result["error_count"] == 0


def test_process_goal_invalid_option():
    """Test that invalid goal option stays at ask_goal."""
    state = create_initial_state("test_user")
    state["current_step"] = "ask_goal"
    state["user_name"] = "João"
    state["user_input"] = "opção inválida"
    
    # Execute process_goal node
    result = process_goal_node(state)
    
    # Verify stays at ask_goal and error count increases
    assert result["investment_goal"] is None
    assert result["current_step"] == "ask_goal"
    assert result["error_count"] == 1
    assert "não entendi" in result["last_message"].lower()
    assert "1) Reserva de emergência" in result["last_message"]
    assert "4) Aprender sobre investimentos" in result["last_message"]


@patch('src.nodes.get_llm')
def test_graph_execution_with_mocked_llm(mock_get_llm):
    """Test full graph execution with mocked LLM."""
    # Mock the LLM response
    mock_llm = Mock()
    mock_response = Mock()
    mock_response.content = "Esta é uma explicação educativa sobre investimentos! 💡"
    mock_llm.invoke.return_value = mock_response
    mock_get_llm.return_value = mock_llm
    
    # Compile graph without checkpointer for testing
    app = compile_journey_graph(checkpointer=None)
    
    # Create initial state
    state = create_initial_state("test_user")
    
    # Simulate user journey
    # Step 1: Start
    result = app.invoke(state)
    assert result["current_step"] == "ask_name"
    
    # Step 2: Provide name
    result["user_input"] = "Maria"
    result = app.invoke(result)
    assert result["user_name"] == "Maria"
    assert result["current_step"] == "ask_goal"
    
    # Step 3: Choose goal
    result["user_input"] = "3"  # Aposentadoria
    result = app.invoke(result)
    assert result["investment_goal"] == "Aposentadoria"
    assert result["current_step"] == "ask_risk_profile"
    
    # Step 4: Choose risk profile
    result["user_input"] = "2"  # Moderado
    result = app.invoke(result)
    assert result["risk_profile"] == "Moderado"
    assert result["current_step"] == "ask_time_horizon"
    
    # Step 5: Choose time horizon
    result["user_input"] = "3"  # Mais de 5 anos
    result = app.invoke(result)
    assert result["time_horizon"] == "Mais de 5 anos"
    
    # Verify LLM was called
    assert mock_llm.invoke.called
    
    # Verify journey completed
    assert result["current_step"] == "end"
    assert result["llm_explanation"] is not None


def test_graph_handles_invalid_input_gracefully():
    """Test that graph handles invalid input without crashing."""
    # Compile graph without checkpointer for testing
    app = compile_journey_graph(checkpointer=None)
    
    # Create initial state
    state = create_initial_state("test_user")
    
    # Start journey
    result = app.invoke(state)
    assert result["current_step"] == "ask_name"
    
    # Provide valid name
    result["user_input"] = "Pedro"
    result = app.invoke(result)
    assert result["current_step"] == "ask_goal"
    
    # Provide invalid goal option
    result["user_input"] = "999"
    result = app.invoke(result)
    
    # Should stay at ask_goal with error
    assert result["current_step"] == "ask_goal"
    assert result["error_count"] == 1
    assert "não entendi" in result["last_message"].lower()
    assert "1) Reserva de emergência" in result["last_message"]
    
    # Provide valid goal option
    result["user_input"] = "1"
    result = app.invoke(result)
    
    # Should advance to ask_risk_profile
    assert result["current_step"] == "ask_risk_profile"
    assert result["error_count"] == 0  # Error count reset
