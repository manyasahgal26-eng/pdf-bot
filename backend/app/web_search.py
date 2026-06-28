import requests
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS


def search_web(query: str, max_results: int = 3) -> list[dict]:
    results = []

    with DDGS() as ddgs:
        for item in ddgs.text(query, max_results=max_results):
            results.append({
                "title": item.get("title"),
                "url": item.get("href"),
                "snippet": item.get("body"),
            })

    return results


def scrape_page(url: str, max_chars: int = 2500) -> str:
    try:
        response = requests.get(
            url,
            timeout=8,
            headers={"User-Agent": "Mozilla/5.0"},
        )
        response.raise_for_status()
    except Exception:
        return ""

    soup = BeautifulSoup(response.text, "html.parser")

    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()

    text = " ".join(soup.get_text(" ").split())
    return text[:max_chars]


def get_web_context(question: str) -> dict:
    search_results = search_web(question)
    contexts = []
    sources = []

    for result in search_results:
        url = result.get("url")
        if not url:
            continue

        page_text = scrape_page(url)

        if page_text:
            contexts.append(page_text)
            sources.append({
                "title": result.get("title"),
                "url": url,
            })

    return {
        "context": "\n\n".join(contexts),
        "sources": sources,
    }