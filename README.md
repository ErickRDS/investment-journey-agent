# Investment Journey Agent

Um agente conversacional CLI que reproduz uma jornada de investimentos usando LangGraph, LangChain e OpenAI.

## 📋 Sobre o Projeto

Este projeto implementa um assistente de investimentos conversacional que guia o usuário através de uma jornada personalizada, coletando informações sobre objetivos financeiros, perfil de risco e horizonte de tempo. O agente usa LLM (OpenAI) para gerar explicações educativas personalizadas.

### Características Principais

- ✅ **CLI Interativo**: Conversa no terminal com interface amigável
- ✅ **Persistência de Estado**: Retoma a conversa de onde parou usando SQLite
- ✅ **LangGraph StateGraph**: Arquitetura explícita com nós e transições
- ✅ **LLM Personalizado**: Usa OpenAI para gerar conteúdo educativo
- ✅ **Comandos Globais**: `voltar`, `recomeçar`, `sair` funcionam em qualquer etapa
- ✅ **Validação de Entrada**: Trata entradas inválidas graciosamente
- ✅ **Testes Automatizados**: Cobertura com pytest incluindo mocks de LLM

## 🏗️ Arquitetura

### Decisão: Caminho B — Grafo Explícito por Etapa

Este projeto implementa a **arquitetura B (Grafo explícito por etapa)** conforme especificado no case técnico.

#### Por que Caminho B?

**Vantagens:**
- ✅ **Clareza**: Cada etapa da jornada é um nó explícito no grafo
- ✅ **Testabilidade**: Fácil testar transições e validações individualmente
- ✅ **Determinismo**: Fluxo previsível e controlado
- ✅ **Manutenibilidade**: Adicionar/modificar etapas é simples e isolado
- ✅ **Debugging**: Logs claros de transições entre nós

**Trade-offs:**
- ❌ **Flexibilidade**: Menos adaptável que um agente baseado puramente em prompts
- ❌ **Conversação Natural**: Não permite desvios arbitrários do fluxo
- ❌ **Escalabilidade**: Adicionar muitas etapas aumenta complexidade do grafo

**Justificativa:**
Para um case técnico focado em **modelagem de jornada**, o Caminho B é ideal porque:
1. Demonstra domínio de LangGraph com StateGraph e conditional edges
2. Facilita validação de requisitos (cada etapa é verificável)
3. Mantém o escopo controlado e testável
4. Permite evolução incremental (adicionar nós sem quebrar o existente)

### Estrutura do Grafo

```
start → ask_name → process_name → ask_goal → process_goal 
  → ask_risk_profile → process_risk_profile → ask_time_horizon 
  → process_time_horizon → explain_concept_with_llm → recommendation → end
```

Cada nó de processamento (`process_*`) valida a entrada e:
- **Se válida**: avança para o próximo nó
- **Se inválida**: retorna ao nó de pergunta anterior

### Componentes

#### 1. State Management (`src/state.py`)
- **TypedDict** para type safety
- Campos obrigatórios e opcionais bem definidos
- Validação de estado

#### 2. LLM Configuration (`src/llm.py`)
- Configuração centralizada do ChatOpenAI
- Leitura de variáveis de ambiente (.env)
- Tratamento de erros de API key

#### 3. Prompts (`src/prompts.py`)
- Separação de conteúdo e lógica
- Prompts reutilizáveis e parametrizados
- Formatação de opções e validação de entrada

#### 4. Checkpoint Persistence (`src/checkpoint.py`)
- **SqliteSaver** do LangGraph
- Persistência automática de estado
- Thread ID por usuário

#### 5. Journey Nodes (`src/nodes.py`)
- Nós de apresentação (mostram mensagens)
- Nós de processamento (validam entrada)
- Nó LLM (gera conteúdo personalizado)
- Tratamento de comandos globais

#### 6. Agent Graph (`src/agent.py`)
- **StateGraph** com nós explícitos
- **add_conditional_edges** para roteamento
- Compilação com checkpointer

#### 7. Main CLI (`main.py`)
- Loop de conversação
- Recuperação de estado persistido
- Tratamento de interrupções (Ctrl+C)

## 🚀 Instalação

### Pré-requisitos

- Python 3.11+
- pip

### Passos

1. **Clone ou navegue até o diretório do projeto:**
```bash
cd investment-journey-agent
```

2. **Crie um ambiente virtual:**
```bash
python -m venv .venv
```

3. **Ative o ambiente virtual:**

Windows:
```bash
.venv\Scripts\activate
```

Linux/Mac:
```bash
source .venv/bin/activate
```

4. **Instale as dependências:**
```bash
pip install -r requirements.txt
```

5. **Configure as variáveis de ambiente:**

Copie o arquivo `.env.example` para `.env`:
```bash
cp .env.example .env
```

Edite o arquivo `.env` e adicione sua chave da OpenAI:
```
OPENAI_API_KEY=sk-sua-chave-aqui
OPENAI_MODEL=gpt-4o-mini
```

## 🎮 Como Usar

### Executar o Agente

```bash
python main.py
```

### Comandos Globais

Durante a conversa, você pode usar estes comandos a qualquer momento:

- **`voltar`**: Retorna ao passo anterior
- **`recomeçar`**: Reinicia a jornada do zero
- **`sair`**: Encerra o programa

### Exemplo de Uso

```
🤖 Investment Journey Agent

Bem-vindo! Este é um agente conversacional que te guia
através de uma jornada de investimentos personalizada.

============================================================
Olá! 👋 Eu sou o Peter, seu assistente de investimentos.

Vou te ajudar a criar uma estratégia de investimentos personalizada, 
aprender sobre finanças e alcançar seus objetivos financeiros.

Vamos começar?
============================================================

Você: sim

============================================================
Primeiro, como você gostaria de ser chamado(a)?

(Digite seu nome)
============================================================

Você: João

============================================================
Ótimo, João! 

Agora me conta: qual é o seu principal objetivo com investimentos?

1) Reserva de emergência
2) Comprar um imóvel
3) Aposentadoria
4) Aprender sobre investimentos
============================================================

Você: 3

[... continua a jornada ...]
```

### Persistência

A conversa é salva automaticamente em `checkpoints.sqlite`. Se você fechar o terminal e executar `python main.py` novamente, a conversa continuará de onde parou!

## 🧪 Testes

### Executar Todos os Testes

```bash
pytest
```

### Executar Testes Específicos

```bash
# Testes de estado
pytest tests/test_state.py

# Testes de transições
pytest tests/test_transitions.py
```

### Executar com Verbose

```bash
pytest -v
```

### Cobertura dos Testes

Os testes incluem:

1. **test_state.py**:
   - Criação de estado inicial
   - Validação de estado
   - Armazenamento de respostas do usuário
   - Rastreamento de progresso
   - Acumulação de histórico

2. **test_transitions.py**:
   - Transições entre nós
   - Validação de entrada válida/inválida
   - Execução completa do grafo com LLM mockado
   - Tratamento de erros

**Importante**: Os testes **não** chamam a API real da OpenAI. O LLM é mockado usando `unittest.mock`.

## 📁 Estrutura de Arquivos

```
investment-journey-agent/
├── README.md                 # Este arquivo
├── requirements.txt          # Dependências Python
├── .env.example             # Exemplo de variáveis de ambiente
├── .gitignore               # Arquivos ignorados pelo Git
├── Dockerfile               # Container Docker (opcional)
├── main.py                  # Ponto de entrada CLI
├── src/
│   ├── __init__.py
│   ├── state.py            # Gerenciamento de estado (TypedDict)
│   ├── llm.py              # Configuração do LLM (OpenAI)
│   ├── prompts.py          # Prompts e mensagens
│   ├── checkpoint.py       # Persistência SQLite
│   ├── nodes.py            # Nós da jornada
│   └── agent.py            # Grafo LangGraph
└── tests/
    ├── __init__.py
    ├── test_state.py       # Testes de estado
    └── test_transitions.py # Testes de transições
```

## 🔧 Tecnologias Utilizadas

- **Python 3.11+**: Linguagem base
- **LangGraph**: Framework para grafos de estado
- **LangChain**: Abstrações para LLMs
- **OpenAI**: Modelo de linguagem (gpt-4o-mini)
- **SQLite**: Persistência de checkpoints
- **pytest**: Framework de testes
- **python-dotenv**: Gerenciamento de variáveis de ambiente
- **Pydantic**: Validação de dados

## 🐳 Docker (Opcional)

Um Dockerfile está incluído para facilitar a execução em container:

```bash
# Build
docker build -t investment-journey-agent .

# Run (interativo)
docker run -it --rm \
  -e OPENAI_API_KEY=sua-chave \
  -v $(pwd)/checkpoints.sqlite:/app/checkpoints.sqlite \
  investment-journey-agent
```

## 📝 Notas Importantes

### O que NÃO está incluído

Este projeto é um **case técnico focado em jornada conversacional CLI**. Intencionalmente **não** inclui:

- ❌ WhatsApp / Twilio / Meta integrations
- ❌ MongoDB ou outros bancos de dados externos
- ❌ Flask / FastAPI / Web UI
- ❌ Deploy em cloud
- ❌ Autenticação / múltiplos usuários
- ❌ Integração com corretoras reais

## 🤝 Contribuindo

Este é um projeto de case técnico, mas sugestões são bem-vindas:

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## 📄 Licença

Este projeto é um case técnico educacional.

## 🙋 Suporte

Para dúvidas ou problemas:
1. Verifique os logs em `journey_agent.log`
2. Confirme que `OPENAI_API_KEY` está configurada
3. Execute os testes: `pytest -v`
4. Verifique se todas as dependências estão instaladas

---

**Desenvolvido como case técnico para demonstrar:**
- Arquitetura de agentes conversacionais com LangGraph
- Modelagem explícita de jornadas com StateGraph
- Persistência de estado com checkpointing
- Integração com LLMs (OpenAI)
- Testes automatizados com mocks
- Boas práticas de Python e engenharia de software