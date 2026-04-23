from pathlib import Path


def build_llm_prompt(dataset_dir, n=10):
    """
    Costruisce un prompt per LLM usando le prime n tracce buone e cattive.

    Args:
        dataset_dir (str | Path): cartella del dataset (contiene tracce_buone/ e tracce_cattive/)
        n (int): numero di tracce da includere nel prompt

    Returns:
        str: prompt pronto per l'LLM
    """
    tracce_buone_dir = Path(dataset_dir) / "tracce_buone"
    tracce_cattive_dir = Path(dataset_dir) / "tracce_cattive"
    buone = [f.read_text(encoding='utf-8').strip() for f in sorted(tracce_buone_dir.iterdir())[:n]]
    cattive = [f.read_text(encoding='utf-8').strip() for f in sorted(tracce_cattive_dir.iterdir())[:n]]
    prompt = (
        f"Ti fornisco una lista di {n} stringhe che la regex deve accettare (positive) "
        f"e {n} che deve rifiutare (negative). "
        "Scrivi una regex Python che accetta tutte le positive e rifiuta tutte le negative. "
        "La regex deve essere plausibile per il parser Python (compilabile senza errori), "
        "non troppo generica (evita regex come '.*', '^.*$', '.+', '^.+$', ecc.), "
        "non troppo lunga (max 200 caratteri). "
        "La regex deve essere il più compatta possibile. Evita soluzioni troppo lunghe o complesse.\n\n"
        "Positive:\n" +
        "\n".join(f"- {s}" for s in buone) +
        "\n\nNegative:\n" +
        "\n".join(f"- {s}" for s in cattive) +
        "\n\nRegex:"
    )
    return prompt


def build_llm_prompt_multi(dataset_dir, n=10, k=5):
    """
    Costruisce un prompt per LLM che chiede k regex diverse.

    Args:
        dataset_dir (str | Path): cartella del dataset
        n (int): numero di tracce da includere per lato
        k (int): numero di regex da chiedere all'LLM

    Returns:
        str: prompt pronto per l'LLM
    """
    tracce_buone_dir = Path(dataset_dir) / "tracce_buone"
    tracce_cattive_dir = Path(dataset_dir) / "tracce_cattive"
    buone = [f.read_text(encoding='utf-8').strip() for f in sorted(tracce_buone_dir.iterdir())[:n]]
    cattive = [f.read_text(encoding='utf-8').strip() for f in sorted(tracce_cattive_dir.iterdir())[:n]]
    prompt = (
        f"Ti fornisco una lista di {n} stringhe che la regex deve accettare (positive) "
        f"e {n} che deve rifiutare (negative). "
        f"Genera {k} regex Python diverse, tutte compatte e facilmente compilabili, "
        "che accettino tutte le positive e rifiutino tutte le negative. "
        "Ogni regex deve essere plausibile per il parser Python (compilabile senza errori), "
        "non troppo generica (evita regex come '.*', '^.*$', '.+', '^.+$', ecc.), "
        "non troppo lunga (max 200 caratteri). "
        "Evita soluzioni troppo lunghe o complesse.\n\n"
        "Positive:\n" +
        "\n".join(f"- {s}" for s in buone) +
        "\n\nNegative:\n" +
        "\n".join(f"- {s}" for s in cattive) +
        "\n\n" +
        "\n".join([f"Regex {i+1}:" for i in range(k)])
    )
    return prompt
