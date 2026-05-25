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
)

logger = logging.getLogger(__name__)


def route_from_start(state: JourneyState) -> Literal["ask_name", "end"]:
    """Route from start node."""
    if state.get("should_exit"):
        return "end"
    return "ask_name"


def route_from_entry(
    state: JourneyState,
) -> Literal[
    "start",
    "ask_name",
    "process_name",
    "ask_goal",
    "process_goal",
    "ask_risk_profile",
    "process_risk_profile",
    "ask_time_horizon",
    "process_time_horizon",
    "explain_concept_with_llm",
    "recommendation",
    "end",
]:
    """Route each invocation from the persisted conversation step."""
    if state.get("should_exit"):
        return "end"

    current_step = state.get("current_step", "start")
    has_input = bool((state.get("user_input") or "").strip())

    if current_step == "ask_name" and has_input:
        return "process_name"
    if current_step == "ask_goal" and has_input:
        return "process_goal"
    if current_step == "ask_risk_profile" and has_input:
        return "process_risk_profile"
    if current_step == "ask_time_horizon" and has_input:
        return "process_time_horizon"

    if current_step in {
        "start",
        "ask_name",
        "ask_goal",
        "ask_risk_profile",
        "ask_time_horizon",
        "explain_concept_with_llm",
        "recommendation",
        "end",
    }:
        return current_step

    return "end"


def route_from_process_name(state: JourneyState) -> str:
    """Route from process_name node based on validation."""
    if state.get("should_exit"):
        return "end"
    
    current_step = state.get("current_step")
    if current_step == "ask_goal":
        return "ask_goal"
    else:
        # Invalid input: keep the validation message set by the process node.
        return END


def route_from_process_goal(state: JourneyState) -> str:
    """Route from process_goal node based on validation."""
    if state.get("should_exit"):
        return "end"
    
    current_step = state.get("current_step")
    if current_step == "ask_risk_profile":
        return "ask_risk_profile"
    else:
        # Invalid input: keep the validation message set by the process node.
        return END


def route_from_process_risk_profile(state: JourneyState) -> str:
    """Route from process_risk_profile node based on validation."""
    if state.get("should_exit"):
        return "end"
    
    current_step = state.get("current_step")
    if current_step == "ask_time_horizon":
        return "ask_time_horizon"
    else:
        # Invalid input: keep the validation message set by the process node.
        return END


def route_from_process_time_horizon(state: JourneyState) -> str:
    """Route from process_time_horizon node based on validation."""
    if state.get("should_exit"):
        return "end"
    
    current_step = state.get("current_step")
    if current_step == "explain_concept_with_llm":
        return "explain_concept_with_llm"
    else:
        # Invalid input: keep the validation message set by the process node.
        return END


def route_from_llm(state: JourneyState) -> Literal["recommendation", "end"]:
    """Route from LLM explanation node."""
    if state.get("should_exit"):
        return "end"
    return "recommendation"


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
    
    # Route each CLI invocation from the current saved step.
    graph.set_conditional_entry_point(route_from_entry)
    
    # Add conditional edges for routing
    graph.add_conditional_edges("start", route_from_start)
    graph.add_conditional_edges("process_name", route_from_process_name)
    graph.add_conditional_edges("process_goal", route_from_process_goal)
    graph.add_conditional_edges("process_risk_profile", route_from_process_risk_profile)
    graph.add_conditional_edges("process_time_horizon", route_from_process_time_horizon)
    graph.add_conditional_edges("explain_concept_with_llm", route_from_llm)
    
    # Prompt nodes should stop after displaying the next question.
    graph.add_edge("ask_name", END)
    graph.add_edge("ask_goal", END)
    graph.add_edge("ask_risk_profile", END)
    graph.add_edge("ask_time_horizon", END)
    graph.add_edge("recommendation", END)
    
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
