"""Main CLI entry point for the investment journey agent."""

import logging
import sys
from src.state import create_initial_state
from src.checkpoint import get_checkpointer, get_thread_id
from src.agent import compile_journey_graph
from src.nodes import handle_global_command
from src.llm import check_llm_available

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("journey_agent.log"),
        logging.StreamHandler(sys.stdout),
    ],
)

logger = logging.getLogger(__name__)


def print_message(message: str):
    """Print message to terminal with formatting."""
    print("\n" + "=" * 60)
    print(message)
    print("=" * 60 + "\n")


def main():
    """Main CLI loop for the investment journey agent."""
    logger.info("Iniciando Investment Journey Agent...")
    
    # Check if LLM is available
    if not check_llm_available():
        print_message(
            "⚠️  ATENÇÃO: OPENAI_API_KEY não encontrada!\n\n"
            "O agente precisa da chave da API OpenAI para funcionar corretamente.\n"
            "Por favor, configure a variável de ambiente no arquivo .env\n\n"
            "Exemplo:\n"
            "OPENAI_API_KEY=sk-...\n"
            "OPENAI_MODEL=gpt-4o-mini"
        )
        sys.exit(1)
    
    # Initialize checkpointer for state persistence
    checkpointer = get_checkpointer()
    
    # Compile the journey graph
    app = compile_journey_graph(checkpointer=checkpointer)
    
    # User ID (in a real app, this would be unique per user)
    user_id = "default_user"
    thread_id = get_thread_id(user_id)
    
    # Configuration for graph invocation
    config = {
        "configurable": {
            "thread_id": thread_id,
        }
    }
    
    print_message(
        "🤖 Investment Journey Agent\n\n"
        "Bem-vindo! Este é um agente conversacional que te guia\n"
        "através de uma jornada de investimentos personalizada.\n\n"
        "Comandos globais disponíveis a qualquer momento:\n"
        "- 'voltar' - Retorna ao passo anterior\n"
        "- 'recomeçar' - Reinicia a jornada do zero\n"
        "- 'sair' - Encerra o programa\n\n"
        "Sua conversa é salva automaticamente. Se você fechar o terminal\n"
        "e executar novamente, continuaremos de onde paramos!"
    )
    
    try:
        # Get or create initial state
        state = None
        try:
            # Try to get existing state from checkpoint
            snapshot = app.get_state(config)
            if snapshot and snapshot.values:
                state = snapshot.values
                logger.info(f"Estado recuperado do checkpoint: step={state.get('current_step')}")
                print_message(
                    "📍 Continuando de onde paramos...\n\n"
                    f"Você estava em: {state.get('current_step')}"
                )
        except Exception as e:
            logger.warning(f"Não foi possível recuperar estado: {e}")
        
        if not state:
            # Create new state
            state = create_initial_state(user_id)
            logger.info("Criando novo estado inicial")
        
        # Main conversation loop
        while not state.get("should_exit", False):
            # Get current step
            current_step = state.get("current_step", "start")
            
            # If we have a message to show, display it
            last_message = state.get("last_message")
            if last_message:
                print_message(last_message)
            
            # If journey ended, break
            if current_step == "end":
                break
            
            # Get user input
            try:
                user_input = input("Você: ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\n")
                logger.info("Usuário interrompeu a execução")
                break
            
            if not user_input:
                continue
            
            # Check for global commands
            state, command_handled = handle_global_command(state, user_input)
            
            if command_handled:
                # If command was handled, update state in graph
                if state.get("should_exit"):
                    msg = state.get("last_message") or "Até logo!"
                    print_message(msg)
                    break
                
                # For restart or back, we need to invoke the graph with updated state
                state["user_input"] = None
                result = app.invoke(state, config)
                state = result
                continue
            
            # Store user input in state
            state["user_input"] = user_input
            
            # Invoke the graph with current state
            logger.info(f"Invocando grafo: step={current_step}, input={user_input[:50]}")
            
            try:
                result = app.invoke(state, config)
                state = result
                logger.info(f"Grafo executado: novo step={state.get('current_step')}")
            except Exception as e:
                logger.error(f"Erro ao executar grafo: {e}", exc_info=True)
                print_message(
                    "❌ Erro ao processar sua mensagem.\n\n"
                    "Por favor, tente novamente ou digite 'recomeçar'."
                )
                continue
        
        # Journey completed
        logger.info("Jornada concluída")
        
    except KeyboardInterrupt:
        print("\n")
        print_message("👋 Até logo! Sua conversa foi salva.")
        logger.info("Programa interrompido pelo usuário")
    except Exception as e:
        logger.error(f"Erro fatal: {e}", exc_info=True)
        print_message(
            f"❌ Erro fatal: {e}\n\n"
            "Por favor, verifique os logs em journey_agent.log"
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
