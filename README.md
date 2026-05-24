# Investment Journey Agent

Agente conversacional em Python que reproduz, no terminal, uma jornada de investimentos inspirada no Peter. A conversa coleta dados do usuário, personaliza as mensagens seguintes e usa um LLM para gerar uma explicação educativa ao final da jornada.

O projeto foi feito para o case técnico de agente conversacional de jornada. Ele roda localmente com `python main.py`, usa LangGraph para modelar o fluxo, persiste o estado da conversa e inclui testes automatizados com `pytest`.

## O Que O Agente Faz

Durante a conversa, o agente:

- se apresenta como Peter, assistente de investimentos;
- pergunta o nome do usuário;
- coleta o objetivo principal de investimento;
- identifica o perfil de risco;
- pergunta o horizonte de tempo;
- chama um LLM para gerar uma explicação educativa personalizada;
- mostra um resumo final da jornada.

As respostas dadas pelo usuário aparecem nas mensagens seguintes, então a jornada não é apenas uma sequência fixa de textos.

## Arquitetura Escolhida

Escolhi o **Caminho B: grafo explícito por etapa**.

Nesse modelo, cada etapa relevante da jornada vira um nó no `StateGraph`. As etapas que recebem input têm um nó de processamento responsável por validar a resposta e decidir o próximo passo. O fluxo principal fica na topologia do grafo, e não escondido em um prompt grande.

Fluxo simplificado:

```text
start
  -> ask_name -> process_name
  -> ask_goal -> process_goal
  -> ask_risk_profile -> process_risk_profile
  -> ask_time_horizon -> process_time_horizon
  -> explain_concept_with_llm
  -> recommendation
  -> end
```

### Por Que Esse Caminho

Esse caminho combina bem com o case porque a jornada tem etapas claras, opções numeradas e validações simples. O grafo explícito deixa fácil enxergar o que acontece em cada momento, testar transições e garantir que uma resposta inválida não avance o usuário para a próxima etapa.

O principal trade-off é que esse desenho é menos livre do que um assistente guiado quase todo por prompt. Ele não tenta transformar qualquer texto livre em conversa aberta; quando uma etapa espera uma opção, o agente valida e reconduz o usuário. Para uma jornada estruturada de onboarding, essa previsibilidade é uma vantagem.

## Principais Decisões Técnicas

- **LangGraph `StateGraph`**: usado para organizar a jornada em nós explícitos.
- **Roteamento com `add_conditional_edges`**: os nós de processamento decidem a próxima etapa depois de validar a resposta do usuário.
- **Estado tipado com `TypedDict`**: o estado fica centralizado em `src/state.py`, sem variável global guardando a conversa.
- **Persistência com `SqliteSaver`**: se o processo for interrompido no meio da jornada, ao rodar novamente o agente retoma do ponto salvo.
- **Jornada finalizada não é retomada**: se o checkpoint salvo já estiver em `end`, o agente inicia uma nova jornada em vez de repetir o resumo final antigo.
- **LLM com OpenAI via LangChain**: uma etapa chama o modelo para gerar conteúdo educativo com base nas respostas coletadas.
- **Fallback de LLM**: se a chamada ao modelo falhar, o agente continua a jornada com uma explicação padrão.
- **Prompts separados**: mensagens, opções e prompts do LLM ficam em `src/prompts.py`.
- **Logging básico**: o projeto registra início, retomada de estado, transições principais, chamadas de LLM e erros.
- **Type hints**: os módulos principais usam anotações de tipo para deixar contratos mais claros.
- **Testes sem chamada real à OpenAI**: o LLM é mockado nos testes.

## Estrutura Do Projeto

```text
investment-journey-agent/
├── main.py                  # Entrada da CLI
├── requirements.txt         # Dependências Python
├── Dockerfile               # Execução opcional via Docker
├── .env.example             # Exemplo de configuração local
├── src/
│   ├── agent.py             # Construção do StateGraph
│   ├── checkpoint.py        # Configuração do checkpointer SQLite
│   ├── llm.py               # Configuração do ChatOpenAI
│   ├── nodes.py             # Nós e comandos da jornada
│   ├── prompts.py           # Textos, opções e prompts
│   └── state.py             # Estado tipado da conversa
└── tests/
    ├── test_state.py        # Testes de estado
    └── test_transitions.py  # Testes de transições do grafo
```

## Como Rodar Localmente

### 1. Criar e ativar o ambiente virtual

```bash
python -m venv .venv
```

No Linux/macOS:

```bash
source .venv/bin/activate
```

No Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 2. Instalar as dependências

```bash
pip install -r requirements.txt
```

### 3. Configurar a chave da OpenAI

Copie o arquivo de exemplo:

```bash
cp .env.example .env
```

Depois preencha o `.env`:

```env
OPENAI_API_KEY=sk-sua-chave-aqui
OPENAI_MODEL=gpt-4o-mini
```

Sem `OPENAI_API_KEY`, o agente não inicia a conversa. Se a chave existir mas a conta estiver sem quota, a etapa de LLM pode falhar com erro da OpenAI; nesse caso o fluxo segue usando o fallback educativo.

### 4. Executar

```bash
python main.py
```

## Comandos Durante A Conversa

Você pode usar estes comandos em qualquer etapa:

- `voltar`: retorna para a etapa anterior;
- `recomeçar`: reinicia a jornada do zero;
- `sair`: encerra o programa.

## Persistência De Estado

A conversa é salva automaticamente em `checkpoints.sqlite`.

Se você fechar o terminal no meio da jornada e rodar `python main.py` de novo, o agente continua do ponto em que parou. Se a jornada anterior já tiver chegado ao fim, o agente inicia uma nova conversa, porque não há mais etapa ativa para retomar.

## Testes

Para rodar a suíte:

```bash
pytest
```

Os testes cobrem criação e validação do estado, transições principais, entradas inválidas, execução completa do grafo e o comportamento de jornadas já finalizadas. A chamada ao LLM é mockada, então os testes não dependem de uma chave real da OpenAI.

## Docker

Também é possível rodar em container:

```bash
docker build -t investment-journey-agent .
docker run -it --rm \
  -e OPENAI_API_KEY=sua-chave \
  -e OPENAI_MODEL=gpt-4o-mini \
  -v "$(pwd)/checkpoints.sqlite:/app/checkpoints.sqlite" \
  investment-journey-agent
```

## O Que Ficou Fora Do Escopo

Seguindo o case, o projeto não inclui:

- integração com WhatsApp, Twilio ou Meta Cloud API;
- MongoDB ou banco externo;
- interface gráfica;
- deploy em cloud;
- integração com corretoras ou recomendações financeiras reais.

O foco aqui é a modelagem da jornada, a persistência de estado, a personalização das respostas e o uso controlado do LLM dentro de uma CLI simples.
