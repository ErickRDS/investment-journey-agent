"""LangGraph agent implementation for the investment journey."""

import logging
from typing import Literal
from langgraph.graph import StateGraph, END
from src.state import JourneyState
from src.nodes import (
    start_node,
    ask_name_node,
    process_name_node,
    ask_goal_node,
    process_goal_node,
    ask_risk_profile_node,
    process_risk_profile_node,
    ask_time_horizon_node,
    process_time_horizon_node,
    explain_concept_with_llm_node,
    recommendation_node,
    end_node,
    fallback_node,
)

logger = logging.getLogger(__name__)


def route_from_start(state: JourneyState) -> Literal["ask_name", "end"]:
    """Route from start node."""
    if state.get("should_exit"):
        return "end"
    return "ask_name"


def route_from_ask_name(state: JourneyState) -> Literal["process_name", "end"]:
    """Route from ask_name node."""
    if state.get("should_exit"):
        return "end"
    return "process_name"


def route_from_process_name(state: JourneyState) -> Literal["ask_name", "ask_goal", "end"]:
    """Route from process_name node based on validation."""
    if state.get("should_exit"):
        return "end"
    
    current_step = state.get("current_step")
    if current_step == "ask_goal":
        return "ask_goal"
    else:
        # Invalid input, stay at ask_name
        return "ask_name"


def route_from_ask_goal(state: JourneyState) -> Literal["process_goal", "end"]:
    """Route from ask_goal node."""
    if state.get("should_exit"):
        return "end"
    return "process_goal"


def route_from_process_goal(state: JourneyState) -> Literal["ask_goal", "ask_risk_profile", "end"]:
    """Route from process_goal node based on validation."""
    if state.get("should_exit"):
        return "end"
    
    current_step = state.get("current_step")
    if current_step == "ask_risk_profile":
        return "ask_risk_profile"
    else:
        # Invalid input, stay at ask_goal
        return "ask_goal"


def route_from_ask_risk_profile(state: JourneyState) -> Literal["process_risk_profile", "end"]:
    """Route from ask_risk_profile node."""
    if state.get("should_exit"):
        return "end"
    return "process_risk_profile"


def route_from_process_risk_profile(state: JourneyState) -> Literal["ask_risk_profile", "ask_time_horizon", "end"]:
    """Route from process_risk_profile node based on validation."""
    if state.get("should_exit"):
        return "end"
    
    current_step = state.get("current_step")
    if current_step == "ask_time_horizon":
        return "ask_time_horizon"
    else:
        # Invalid input, stay at ask_risk_profile
        return "ask_risk_profile"


def route_from_ask_time_horizon(state: JourneyState) -> Literal["process_time_horizon", "end"]:
    """Route from ask_time_horizon node."""
    if state.get("should_exit"):
        return "end"
    return "process_time_horizon"


def route_from_process_time_horizon(state: JourneyState) -> Literal["ask_time_horizon", "explain_concept_with_llm", "end"]:
    """Route from process_time_horizon node based on validation."""
    if state.get("should_exit"):
        return "end"
    
    current_step = state.get("current_step")
    if current_step == "explain_concept_with_llm":
        return "explain_concept_with_llm"
    else:
        # Invalid input, stay at ask_time_horizon
        return "ask_time_horizon"


def route_from_llm(state: JourneyState) -> Literal["recommendation", "end"]:
    """Route from LLM explanation node."""
    if state.get("should_exit"):
        return "end"
    return "recommendation"


def route_from_recommendation(state: JourneyState) -> Literal["end"]:
    """Route from recommendation node."""
    return "end"


def create_journey_graph() -> StateGraph:
    """
    Create the LangGraph StateGraph for the investment journey.
    
    This implements "Caminho B — Grafo explícito por etapa" where each
    journey step is modeled as an explicit node with conditional edges
    for routing.
    
    Returns:
        Configured StateGraph ready to compile
    """
    logger.info("Creating journey graph...")
    
    # Create the graph with JourneyState
    graph = StateGraph(JourneyState)
    
    # Add all nodes
    graph.add_node("start", start_node)
    graph.add_node("ask_name", ask_name_node)
    graph.add_node("process_name", process_name_node)
    graph.add_node("ask_goal", ask_goal_node)
    graph.add_node("process_goal", process_goal_node)
    graph.add_node("ask_risk_profile", ask_risk_profile_node)
    graph.add_node("process_risk_profile", process_risk_profile_node)
    graph.add_node("ask_time_horizon", ask_time_horizon_node)
    graph.add_node("process_time_horizon", process_time_horizon_node)
    graph.add_node("explain_concept_with_llm", explain_concept_with_llm_node)
    graph.add_node("recommendation", recommendation_node)
    graph.add_node("end", end_node)
    graph.add_node("fallback", fallback_node)
    
    # Set entry point
    graph.set_entry_point("start")
    
    # Add conditional edges for routing
    graph.add_conditional_edges("start", route_from_start)
    graph.add_conditional_edges("ask_name", route_from_ask_name)
    graph.add_conditional_edges("process_name", route_from_process_name)
    graph.add_conditional_edges("ask_goal", route_from_ask_goal)
    graph.add_conditional_edges("process_goal", route_from_process_goal)
    graph.add_conditional_edges("ask_risk_profile", route_from_ask_risk_profile)
    graph.add_conditional_edges("process_risk_profile", route_from_process_risk_profile)
    graph.add_conditional_edges("ask_time_horizon", route_from_ask_time_horizon)
    graph.add_conditional_edges("process_time_horizon", route_from_process_time_horizon)
    graph.add_conditional_edges("explain_concept_with_llm", route_from_llm)
    graph.add_conditional_edges("recommendation", route_from_recommendation)
    
    # End node terminates the graph
    graph.add_edge("end", END)
    
    logger.info("Journey graph created successfully")
    
    return graph


def compile_journey_graph(checkpointer=None):
    """
    Compile the journey graph with optional checkpointer.
    
    Args:
        checkpointer: Optional checkpointer for state persistence
        
    Returns:
        Compiled graph ready to invoke
    """
    graph = create_journey_graph()
    
    if checkpointer:
        logger.info("Compiling graph with checkpointer")
        return graph.compile(checkpointer=checkpointer)
    else:
        logger.info("Compiling graph without checkpointer")
        return graph.compile()
