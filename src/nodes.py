"""Journey nodes for the investment journey agent."""

import logging
from typing import Literal
from src.state import JourneyState
from src.prompts import (
    WELCOME_MESSAGE,
    ASK_NAME_PROMPT,
    ASK_GOAL_PROMPT,
    ASK_GOAL_OPTIONS,
    ASK_RISK_PROMPT,
    ASK_RISK_OPTIONS,
    ASK_TIME_HORIZON_PROMPT,
    ASK_TIME_HORIZON_OPTIONS,
    EDUCATIONAL_EXPLANATION_PROMPT,
    RECOMMENDATION_SUMMARY,
    FALLBACK_INVALID_OPTION,
    EXIT_MESSAGE,
    RESTART_MESSAGE,
    BACK_MESSAGE,
    format_options,
    get_option_value,
)
from src.llm import get_llm

logger = logging.getLogger(__name__)


def start_node(state: JourneyState) -> JourneyState:
    """
    Start node - welcomes the user and begins the journey.
    
    Args:
        state: Current journey state
        
    Returns:
        Updated state with welcome message
    """
    logger.info(f"[start_node] User: {state['user_id']}")
    
    state["last_message"] = WELCOME_MESSAGE
    state["current_step"] = "ask_name"
    state["previous_step"] = "start"
    state["history"].append({"step": "start", "message": WELCOME_MESSAGE})
    
    return state


def ask_name_node(state: JourneyState) -> JourneyState:
    """
    Ask for user's name.
    
    Args:
        state: Current journey state
        
    Returns:
        Updated state with name prompt
    """
    logger.info(f"[ask_name_node] User: {state['user_id']}")
    
    state["last_message"] = ASK_NAME_PROMPT
    state["current_step"] = "ask_name"
    state["previous_step"] = "start"
    state["history"].append({"step": "ask_name", "message": ASK_NAME_PROMPT})
    
    return state


def process_name_node(state: JourneyState) -> JourneyState:
    """
    Process the user's name input.
    
    Args:
        state: Current journey state with user_input
        
    Returns:
        Updated state with stored name
    """
    user_input = (state.get("user_input") or "").strip()
    logger.info(f"[process_name_node] User: {state['user_id']}, Input: {user_input}")
    
    if user_input:
        # Capitalize first letter of each word
        state["user_name"] = user_input.title()
        state["current_step"] = "ask_goal"
        state["previous_step"] = "ask_name"
        state["error_count"] = 0
    else:
        # Invalid input
        state["error_count"] = state.get("error_count", 0) + 1
        state["last_message"] = "Por favor, digite seu nome."
        state["current_step"] = "ask_name"
    
    return state


def ask_goal_node(state: JourneyState) -> JourneyState:
    """
    Ask for user's investment goal.
    
    Args:
        state: Current journey state
        
    Returns:
        Updated state with goal prompt
    """
    logger.info(f"[ask_goal_node] User: {state['user_id']}")
    
    name = state.get("user_name", "")
    message = ASK_GOAL_PROMPT.format(name=name) + "\n\n" + format_options(ASK_GOAL_OPTIONS)
    
    state["last_message"] = message
    state["current_step"] = "ask_goal"
    state["previous_step"] = "ask_name"
    state["history"].append({"step": "ask_goal", "message": message})
    
    return state


def process_goal_node(state: JourneyState) -> JourneyState:
    """
    Process the user's investment goal input.
    
    Args:
        state: Current journey state with user_input
        
    Returns:
        Updated state with stored goal
    """
    user_input = (state.get("user_input") or "").strip()
    logger.info(f"[process_goal_node] User: {state['user_id']}, Input: {user_input}")
    
    goal = get_option_value(ASK_GOAL_OPTIONS, user_input)
    
    if goal:
        state["investment_goal"] = goal
        state["current_step"] = "ask_risk_profile"
        state["previous_step"] = "ask_goal"
        state["error_count"] = 0
    else:
        # Invalid option
        state["error_count"] = state.get("error_count", 0) + 1
        state["last_message"] = FALLBACK_INVALID_OPTION
        state["current_step"] = "ask_goal"
    
    return state


def ask_risk_profile_node(state: JourneyState) -> JourneyState:
    """
    Ask for user's risk profile.
    
    Args:
        state: Current journey state
        
    Returns:
        Updated state with risk profile prompt
    """
    logger.info(f"[ask_risk_profile_node] User: {state['user_id']}")
    
    name = state.get("user_name", "")
    goal = state.get("investment_goal", "")
    message = ASK_RISK_PROMPT.format(name=name, goal=goal) + "\n\n" + format_options(ASK_RISK_OPTIONS)
    
    state["last_message"] = message
    state["current_step"] = "ask_risk_profile"
    state["previous_step"] = "ask_goal"
    state["history"].append({"step": "ask_risk_profile", "message": message})
    
    return state


def process_risk_profile_node(state: JourneyState) -> JourneyState:
    """
    Process the user's risk profile input.
    
    Args:
        state: Current journey state with user_input
        
    Returns:
        Updated state with stored risk profile
    """
    user_input = (state.get("user_input") or "").strip()
    logger.info(f"[process_risk_profile_node] User: {state['user_id']}, Input: {user_input}")
    
    risk = get_option_value(ASK_RISK_OPTIONS, user_input)
    
    if risk:
        # Extract just the profile name (before the dash)
        profile_name = risk.split(" - ")[0]
        state["risk_profile"] = profile_name
        state["current_step"] = "ask_time_horizon"
        state["previous_step"] = "ask_risk_profile"
        state["error_count"] = 0
    else:
        # Invalid option
        state["error_count"] = state.get("error_count", 0) + 1
        state["last_message"] = FALLBACK_INVALID_OPTION
        state["current_step"] = "ask_risk_profile"
    
    return state


def ask_time_horizon_node(state: JourneyState) -> JourneyState:
    """
    Ask for user's time horizon.
    
    Args:
        state: Current journey state
        
    Returns:
        Updated state with time horizon prompt
    """
    logger.info(f"[ask_time_horizon_node] User: {state['user_id']}")
    
    risk_profile = state.get("risk_profile", "")
    message = ASK_TIME_HORIZON_PROMPT.format(risk_profile=risk_profile) + "\n\n" + format_options(ASK_TIME_HORIZON_OPTIONS)
    
    state["last_message"] = message
    state["current_step"] = "ask_time_horizon"
    state["previous_step"] = "ask_risk_profile"
    state["history"].append({"step": "ask_time_horizon", "message": message})
    
    return state


def process_time_horizon_node(state: JourneyState) -> JourneyState:
    """
    Process the user's time horizon input.
    
    Args:
        state: Current journey state with user_input
        
    Returns:
        Updated state with stored time horizon
    """
    user_input = (state.get("user_input") or "").strip()
    logger.info(f"[process_time_horizon_node] User: {state['user_id']}, Input: {user_input}")
    
    horizon = get_option_value(ASK_TIME_HORIZON_OPTIONS, user_input)
    
    if horizon:
        # Extract just the horizon description (before the dash)
        horizon_name = horizon.split(" - ")[0]
        state["time_horizon"] = horizon_name
        state["current_step"] = "explain_concept_with_llm"
        state["previous_step"] = "ask_time_horizon"
        state["error_count"] = 0
    else:
        # Invalid option
        state["error_count"] = state.get("error_count", 0) + 1
        state["last_message"] = FALLBACK_INVALID_OPTION
        state["current_step"] = "ask_time_horizon"
    
    return state


def explain_concept_with_llm_node(state: JourneyState) -> JourneyState:
    """
    Use LLM to generate personalized educational explanation.
    
    This is the required LLM step that uses OpenAI to create
    a personalized message based on user's collected data.
    
    Args:
        state: Current journey state
        
    Returns:
        Updated state with LLM-generated explanation
    """
    logger.info(f"[explain_concept_with_llm_node] User: {state['user_id']}")
    
    try:
        llm = get_llm(temperature=0.7)
        
        prompt = EDUCATIONAL_EXPLANATION_PROMPT.format(
            user_name=state.get("user_name", ""),
            investment_goal=state.get("investment_goal", ""),
            risk_profile=state.get("risk_profile", ""),
            time_horizon=state.get("time_horizon", ""),
        )
        
        logger.info("[explain_concept_with_llm_node] Chamando LLM...")
        response = llm.invoke(prompt)
        explanation = response.content.strip()
        
        logger.info(f"[explain_concept_with_llm_node] LLM response: {explanation[:100]}...")
        
        # Store explanation in state for use in recommendation
        state["llm_explanation"] = explanation
        state["current_step"] = "recommendation"
        state["previous_step"] = "explain_concept_with_llm"
        
    except Exception as e:
        logger.error(f"[explain_concept_with_llm_node] Erro ao chamar LLM: {e}")
        # Fallback explanation if LLM fails
        state["llm_explanation"] = (
            "Entender seu perfil é essencial para construir uma estratégia "
            "de investimentos que faça sentido para você! 💡"
        )
        state["current_step"] = "recommendation"
        state["previous_step"] = "explain_concept_with_llm"
    
    return state


def recommendation_node(state: JourneyState) -> JourneyState:
    """
    Show final recommendation summary.
    
    Args:
        state: Current journey state
        
    Returns:
        Updated state with recommendation message
    """
    logger.info(f"[recommendation_node] User: {state['user_id']}")
    
    message = RECOMMENDATION_SUMMARY.format(
        name=state.get("user_name", ""),
        goal=state.get("investment_goal", ""),
        risk_profile=state.get("risk_profile", ""),
        time_horizon=state.get("time_horizon", ""),
        llm_explanation=state.get("llm_explanation", ""),
    )
    
    state["last_message"] = message
    state["current_step"] = "end"
    state["previous_step"] = "recommendation"
    state["history"].append({"step": "recommendation", "message": message})
    
    return state


def end_node(state: JourneyState) -> JourneyState:
    """
    End node - marks journey as complete.
    
    Args:
        state: Current journey state
        
    Returns:
        Updated state marked for exit
    """
    logger.info(f"[end_node] User: {state['user_id']}")
    
    state["last_message"] = EXIT_MESSAGE
    state["current_step"] = "end"
    state["should_exit"] = True
    state["history"].append({"step": "end", "message": EXIT_MESSAGE})
    
    return state


def fallback_node(state: JourneyState) -> JourneyState:
    """
    Fallback node for handling errors or invalid states.
    
    Args:
        state: Current journey state
        
    Returns:
        Updated state with fallback message
    """
    logger.warning(f"[fallback_node] User: {state['user_id']}, Step: {state.get('current_step')}")
    
    state["last_message"] = FALLBACK_INVALID_OPTION
    state["error_count"] = state.get("error_count", 0) + 1
    
    # If too many errors, suggest restart
    if state["error_count"] >= 3:
        state["last_message"] += "\n\nParece que algo não está funcionando. Digite 'recomeçar' para tentar novamente."
    
    return state


def handle_global_command(state: JourneyState, command: str) -> tuple[JourneyState, bool]:
    """
    Handle global commands (voltar, recomeçar, sair).
    
    Args:
        state: Current journey state
        command: User command
        
    Returns:
        Tuple of (updated state, command_handled)
    """
    command = command.strip().lower()
    
    if command == "sair":
        logger.info(f"[handle_global_command] User {state['user_id']} exiting")
        state["should_exit"] = True
        state["last_message"] = EXIT_MESSAGE
        return state, True
    
    elif command == "recomeçar" or command == "recomecar":
        logger.info(f"[handle_global_command] User {state['user_id']} restarting")
        # Reset journey but keep user_id
        user_id = state["user_id"]
        from src.state import create_initial_state
        state = create_initial_state(user_id)
        state["last_message"] = RESTART_MESSAGE + "\n\n" + WELCOME_MESSAGE
        state["current_step"] = "ask_name"
        return state, True
    
    elif command == "voltar":
        logger.info(f"[handle_global_command] User {state['user_id']} going back")
        previous = state.get("previous_step")
        if previous and previous != "start":
            state["current_step"] = previous
            state["last_message"] = BACK_MESSAGE
            state["error_count"] = 0
            return state, True
        else:
            state["last_message"] = "Você já está no início da jornada."
            return state, True
    
    return state, False
