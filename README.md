# Stardew Valley Assistant

Assistente de chat para Stardew Valley baseado em RAG sobre a wiki oficial. Responde perguntas, dá dicas e ajuda a planejar o progresso no jogo.

## Stack

- **LLM + Embeddings:** [Ollama](https://ollama.com) (llama3.2 + nomic-embed-text)
- **Vector store:** ChromaDB
- **Fonte de dados:** [Stardew Valley Wiki](https://stardewvalleywiki.com)

## Setup

**1. Instalar Ollama e baixar os modelos**

```bash
brew install ollama
ollama pull llama3.2
ollama pull nomic-embed-text
```

**2. Instalar dependências Python**

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**3. Scrape da wiki**

```bash
python3 scraper.py
```

**4. Indexar no ChromaDB**

```bash
python3 ingest.py
```

**5. Rodar o assistente**

```bash
python3 chat.py
```

## Uso

Digite sua pergunta normalmente. Comandos especiais:

- `/estado` — informa seu progresso atual (ano, dia, ouro, bundles pendentes) para respostas mais contextuais
- `/sair` — encerrar
