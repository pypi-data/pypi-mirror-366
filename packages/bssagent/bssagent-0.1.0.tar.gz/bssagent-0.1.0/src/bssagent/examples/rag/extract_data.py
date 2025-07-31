from bssagent.rag.text_extractor import extract_text_from_mixed_sources


def extract_data(sources: list[dict]) -> list[dict]:
    """Extract data from mixed sources."""
    return extract_text_from_mixed_sources(sources)



if __name__ == "__main__":
    sources = [
        {"type": "url", "url": "https://example.com"},
    ]
    print(extract_data(sources))