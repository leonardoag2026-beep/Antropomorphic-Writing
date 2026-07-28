import httpx
from deep_translator import GoogleTranslator


def google_translate(text: str, source: str, target: str) -> str:
    translator = GoogleTranslator(source=source, target=target)
    if len(text) > 4500:
        chunks = _split_text(text, max_len=4500)
        return " ".join(translator.translate(chunk) for chunk in chunks)
    return translator.translate(text)


def niutrans_web_translate(text: str, source: str = "fi", target: str = "en") -> str:
    if len(text) > 5000:
        chunks = _split_text(text, max_len=4500)
        return " ".join(
            niutrans_web_translate(chunk, source=source, target=target)
            for chunk in chunks
        )
    response = httpx.get(
        "https://test.niutrans.com/NiuTransServer/testtrans",
        params={
            "query": "25462728",
            "from": source,
            "to": target,
            "src_text": text,
            "source": "text",
        },
        headers={
            "User-Agent": "Mozilla/5.0",
            "Origin": "https://translate.niutrans.com",
            "Referer": "https://translate.niutrans.com/",
        },
        timeout=30,
    )
    response.raise_for_status()
    data = response.json()
    if "tgt_text" in data:
        return data["tgt_text"]
    raise RuntimeError(f"Niutrans web error: {data}")


def _split_text(text: str, max_len: int = 4500) -> list[str]:
    import re
    sentences = re.split(r'(?<=[.!?。！？])\s+', text)
    chunks = []
    current = ""
    for sentence in sentences:
        if len(current) + len(sentence) + 1 > max_len:
            if current:
                chunks.append(current)
            current = sentence
        else:
            current = f"{current} {sentence}".strip()
    if current:
        chunks.append(current)
    return chunks if chunks else [text]
