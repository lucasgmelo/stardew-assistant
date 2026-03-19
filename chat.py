"""
Assistente de Stardew Valley — interface terminal.
RAG: ChromaDB + nomic-embed-text + llama3.2 via Ollama.
"""

import chromadb
from langchain_ollama import OllamaEmbeddings, OllamaLLM
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from config import CHROMA_PATH, COLLECTION_NAME, EMBED_MODEL, LLM_MODEL

console = Console()

def build_prompt(context: str, question: str, game_state: str) -> str:
    return f"""Você é um guia experiente de Stardew Valley. Responda em português, de forma prática e direta.
Use as informações da wiki abaixo para embasar sua resposta. Se não souber algo, diga claramente.

Estado atual do jogador:
{game_state if game_state else "Não informado"}

Informações relevantes da wiki:
{context}

Pergunta: {question}

Resposta (use markdown para organizar se necessário):"""


def retrieve(collection, embeddings_model, query: str, k: int = 6) -> list[dict]:
    query_embedding = embeddings_model.embed_query(query)
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=k,
        include=["documents", "metadatas", "distances"],
    )
    chunks = []
    for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        chunks.append({"text": doc, "meta": meta, "score": 1 - dist})
    return chunks


def format_context(chunks: list[dict]) -> str:
    parts = []
    for c in chunks:
        source = c["meta"].get("title", "Wiki")
        parts.append(f"[{source}]\n{c['text']}")
    return "\n\n---\n\n".join(parts)


def show_sources(chunks: list[dict]):
    seen = set()
    sources = []
    for c in chunks:
        title = c["meta"].get("title", "?")
        if title not in seen:
            seen.add(title)
            sources.append(f"  • {title} (relevância: {c['score']:.2f})")
    console.print("\n[dim]Fontes consultadas:[/dim]")
    for s in sources:
        console.print(f"[dim]{s}[/dim]")


def ask(collection, embeddings_model, llm, question: str, game_state: str) -> str:
    chunks = retrieve(collection, embeddings_model, question)
    context = format_context(chunks)
    prompt = build_prompt(context, question, game_state)
    answer = llm.invoke(prompt)
    show_sources(chunks)
    return answer


def update_game_state(current: str) -> str:
    console.print("\n[yellow]Estado atual do jogador:[/yellow]")
    console.print(f"[dim]{current if current else 'Nenhum'}[/dim]")
    console.print("[yellow]Digite o novo estado (ou Enter para manter):[/yellow]")
    console.print("[dim]Exemplo: Ano 1, Verão dia 5. Tenho 10k gold. Falta: vault bundles.[/dim]")
    new_state = input("> ").strip()
    return new_state if new_state else current


def main():
    console.print(Panel.fit(
        "[bold green]Stardew Valley Assistant[/bold green]\n"
        "[dim]RAG sobre a wiki oficial • Powered by Ollama[/dim]",
        border_style="green",
    ))

    console.print("\n[dim]Conectando ao ChromaDB...[/dim]")
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    collection = client.get_collection(COLLECTION_NAME)
    console.print(f"[dim]Coleção carregada: {collection.count()} chunks[/dim]")

    console.print(f"[dim]Carregando modelos Ollama ({EMBED_MODEL}, {LLM_MODEL})...[/dim]")
    embeddings_model = OllamaEmbeddings(model=EMBED_MODEL)
    llm = OllamaLLM(model=LLM_MODEL, temperature=0.3)

    game_state = ""

    console.print("\n[bold]Comandos especiais:[/bold]")
    console.print("  [cyan]/estado[/cyan]  — atualizar seu estado no jogo (ano, dia, ouro, progresso)")
    console.print("  [cyan]/sair[/cyan]    — encerrar")
    console.print()

    while True:
        try:
            question = input("Você: ").strip()
        except (EOFError, KeyboardInterrupt):
            console.print("\n[yellow]Até logo, fazendeiro![/yellow]")
            break

        if not question:
            continue

        if question.lower() in ("/sair", "/quit", "/exit"):
            console.print("[yellow]Até logo, fazendeiro![/yellow]")
            break

        if question.lower() == "/estado":
            game_state = update_game_state(game_state)
            console.print(f"[green]Estado atualizado![/green]")
            continue

        console.print("[dim]Pensando...[/dim]")
        try:
            answer = ask(collection, embeddings_model, llm, question, game_state)
            console.print()
            console.print(Markdown(answer))
            console.print()
        except Exception as e:
            console.print(f"[red]Erro: {e}[/red]")


if __name__ == "__main__":
    main()
