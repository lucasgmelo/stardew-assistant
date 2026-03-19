"""
Scrape da wiki do Stardew Valley.
Salva cada página como arquivo .txt em ./wiki_pages/
"""

import os
import time
import json
import requests
from bs4 import BeautifulSoup
from config import WIKI_BASE, WIKI_PAGES

OUTPUT_DIR = "./wiki_pages"
METADATA_FILE = "./wiki_pages/metadata.json"


def fetch_page(path: str) -> dict | None:
    url = WIKI_BASE + path
    try:
        resp = requests.get(url, timeout=15, headers={"User-Agent": "StardewRAG/1.0"})
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"  ERRO ao buscar {url}: {e}")
        return None

    soup = BeautifulSoup(resp.text, "html.parser")

    # Remove elementos que poluem o texto
    for tag in soup.select("script, style, .navbox, .toc, #toc, .mw-editsection, "
                           ".catlinks, #catlinks, .printfooter, .mw-references-wrap"):
        tag.decompose()

    # Pega só o conteúdo principal do artigo
    content_div = soup.select_one("#mw-content-text .mw-parser-output")
    if not content_div:
        content_div = soup.select_one("#mw-content-text")
    if not content_div:
        print(f"  AVISO: conteúdo não encontrado em {url}")
        return None

    title = soup.select_one("#firstHeading")
    title_text = title.get_text(strip=True) if title else path.strip("/").replace("_", " ")

    # Extrai texto preservando estrutura de seções
    lines = []
    for elem in content_div.children:
        if not hasattr(elem, "get_text"):
            continue
        tag = getattr(elem, "name", None)
        text = elem.get_text(separator=" ", strip=True)
        if not text:
            continue
        if tag in ("h1", "h2", "h3", "h4"):
            lines.append(f"\n## {text}\n")
        else:
            lines.append(text)

    full_text = "\n".join(lines).strip()

    return {
        "title": title_text,
        "url": url,
        "path": path,
        "text": full_text,
    }


def slug(path: str) -> str:
    return path.strip("/").replace("/", "_").replace(" ", "_")


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    metadata = []

    total = len(WIKI_PAGES)
    for i, path in enumerate(WIKI_PAGES, 1):
        filename = f"{slug(path)}.txt"
        filepath = os.path.join(OUTPUT_DIR, filename)

        if os.path.exists(filepath):
            print(f"[{i}/{total}] Pulando (já existe): {path}")
            continue

        print(f"[{i}/{total}] Scraping: {path}")
        page = fetch_page(path)
        if page is None:
            continue

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"# {page['title']}\n\n")
            f.write(f"Fonte: {page['url']}\n\n")
            f.write(page["text"])

        metadata.append({
            "file": filename,
            "title": page["title"],
            "url": page["url"],
            "path": path,
        })

        time.sleep(0.5)  # respeitar o servidor

    # Atualiza metadata acumulando com possíveis execuções anteriores
    existing = []
    if os.path.exists(METADATA_FILE):
        with open(METADATA_FILE) as f:
            existing = json.load(f)
    existing_files = {m["file"] for m in existing}
    combined = existing + [m for m in metadata if m["file"] not in existing_files]

    with open(METADATA_FILE, "w", encoding="utf-8") as f:
        json.dump(combined, f, ensure_ascii=False, indent=2)

    print(f"\nConcluído. {len(metadata)} novas páginas salvas em {OUTPUT_DIR}/")
    print(f"Total no índice: {len(combined)} páginas")


if __name__ == "__main__":
    main()
