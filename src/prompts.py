"""Prompts for the investment journey agent."""

from typing import Dict


# System prompt for Peter's personality
PETER_SYSTEM_PROMPT = """Você é o Peter, um assistente de investimentos AI amigável e educativo.

Seu papel é guiar o usuário através de uma jornada de investimentos personalizada, 
coletando informações sobre seus objetivos, perfil de risco e horizonte de tempo.

Tom de voz:
- Direto, respeitoso e natural
- Use emojis com moderação (máximo 1 por mensagem)
- Seja educativo mas não técnico demais
- Adapte-se ao contexto do usuário

Formatação:
- Mantenha mensagens curtas e objetivas
- Use bullets quando listar opções
- Seja claro e fácil de entender no terminal
"""


# Welcome message
WELCOME_MESSAGE = """Olá! 👋 Eu sou o Peter, seu assistente de investimentos.

Vou te ajudar a criar uma estratégia de investimentos personalizada, 
aprender sobre finanças e alcançar seus objetivos financeiros.

Vamos começar?"""


# Prompt for name collection
ASK_NAME_PROMPT = """Primeiro, como você gostaria de ser chamado(a)?

(Digite seu nome)"""


# Prompt for investment goal
ASK_GOAL_PROMPT = """Ótimo, {name}! 

Agora me conta: qual é o seu principal objetivo com investimentos?"""

ASK_GOAL_OPTIONS = {
    "1": "Reserva de emergência",
    "2": "Comprar um imóvel",
    "3": "Aposentadoria",
    "4": "Aprender sobre investimentos",
}


# Prompt for risk profile
ASK_RISK_PROMPT = """Entendi, {name}. Seu objetivo é: {goal}

Agora preciso entender seu perfil de risco. Como você se sente em relação a investimentos?"""

ASK_RISK_OPTIONS = {
    "1": "Conservador - Prefiro segurança, mesmo com menor retorno",
    "2": "Moderado - Aceito algum risco para ter retornos melhores",
    "3": "Arrojado - Busco maiores retornos, aceito mais risco",
}


# Prompt for time horizon
ASK_TIME_HORIZON_PROMPT = """Perfeito! Você tem um perfil {risk_profile}.

Qual é o seu horizonte de tempo para esse objetivo?"""

ASK_TIME_HORIZON_OPTIONS = {
    "1": "Até 1 ano - Curto prazo",
    "2": "1 a 5 anos - Médio prazo",
    "3": "Mais de 5 anos - Longo prazo",
}


# LLM prompt for educational explanation
EDUCATIONAL_EXPLANATION_PROMPT = """Você é o Peter, um assistente de investimentos educativo e amigável.

Com base nas informações do usuário, crie uma explicação curta e personalizada (máximo 300 caracteres) 
sobre por que o objetivo, perfil de risco e horizonte de tempo são importantes para a estratégia de investimentos.

Informações do usuário:
- Nome: {user_name}
- Objetivo: {investment_goal}
- Perfil de risco: {risk_profile}
- Horizonte de tempo: {time_horizon}

Seja direto, educativo e motivador. Use linguagem simples e um emoji no máximo."""


# Recommendation summary
RECOMMENDATION_SUMMARY = """Excelente, {name}! 🎯

Com base no que conversamos:
- Objetivo: {goal}
- Perfil: {risk_profile}
- Horizonte: {time_horizon}

{llm_explanation}

Essa foi uma jornada inicial para entender seu perfil. 
Em uma aplicação real, eu te ajudaria a montar uma carteira personalizada!

Obrigado por conhecer o Peter! 😊"""


# Fallback messages
FALLBACK_INVALID_OPTION = """Desculpe, não entendi essa opção. 

Por favor, escolha uma das opções disponíveis digitando o número correspondente.

Você também pode usar os comandos:
- 'voltar' para retornar ao passo anterior
- 'recomeçar' para reiniciar a jornada
- 'sair' para encerrar"""


FALLBACK_ERROR = """Ops! Algo deu errado. 😅

Vamos tentar novamente. Digite 'recomeçar' para começar do zero 
ou 'sair' para encerrar."""


# Exit message
EXIT_MESSAGE = """Até logo! 👋

Quando quiser retomar a conversa, é só executar o programa novamente. 
Vou lembrar de onde paramos!"""


# Restart message
RESTART_MESSAGE = """Tudo bem! Vamos recomeçar do início. 🔄"""


# Back message
BACK_MESSAGE = """Voltando ao passo anterior..."""


def format_options(options: Dict[str, str]) -> str:
    """
    Format options dictionary as numbered list.
    
    Args:
        options: Dictionary with option number as key and description as value
        
    Returns:
        Formatted string with numbered options
    """
    lines = []
    for num, desc in options.items():
        lines.append(f"{num}) {desc}")
    return "\n".join(lines)


def get_option_value(options: Dict[str, str], user_input: str) -> str | None:
    """
    Get option value from user input (number or text).
    
    Args:
        options: Dictionary with option number as key and description as value
        user_input: User's input (can be number or option text)
        
    Returns:
        Option description if found, None otherwise
    """
    user_input = user_input.strip().lower()
    
    # Try direct number match
    if user_input in options:
        return options[user_input]
    
    # Try matching option text
    for num, desc in options.items():
        if user_input in desc.lower():
            return desc
    
    return None
