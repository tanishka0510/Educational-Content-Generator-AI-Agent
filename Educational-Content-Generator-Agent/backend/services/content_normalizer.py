from typing import Any, Dict, List


def normalize_content(response: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(response, dict):
        raise ValueError(
            "Content Processing Agent response must be a dictionary."
        )

    summary = response.get("summary", "")
    learning_objectives = response.get("learning_objectives", [])
    keywords = response.get("keywords", [])
    concepts = response.get("concepts", [])
    difficulty = response.get("difficulty", "Unknown")
    sources = response.get("sources", [])
    retrieval_score = response.get("retrieval_score")

    if summary is None:
        summary = ""

    if not isinstance(summary, str):
        summary = str(summary)

    if not isinstance(learning_objectives, list):
        learning_objectives = [learning_objectives]

    if not isinstance(keywords, list):
        keywords = [keywords]

    if not isinstance(concepts, list):
        concepts = [concepts]

    if not isinstance(sources, list):
        sources = [sources]

    learning_objectives = [
        str(item).strip()
        for item in learning_objectives
        if item is not None and str(item).strip()
    ]

    keywords = [
        str(item).strip()
        for item in keywords
        if item is not None and str(item).strip()
    ]

    concepts = [
        str(item).strip()
        for item in concepts
        if item is not None and str(item).strip()
    ]

    sources = [
        str(item).strip()
        for item in sources
        if item is not None and str(item).strip()
    ]

    if difficulty is None:
        difficulty = "Unknown"
    else:
        difficulty = str(difficulty).strip()

        if not difficulty:
            difficulty = "Unknown"

    return {
        "summary": summary.strip(),
        "learning_objectives": learning_objectives,
        "keywords": keywords,
        "concepts": concepts,
        "difficulty": difficulty,
        "sources": sources,
        "retrieval_score": retrieval_score,
    }


def content_to_text(content: Dict[str, Any]) -> str:
    normalized = normalize_content(content)

    sections: List[str] = []

    if normalized["summary"]:
        sections.append(
            "SUMMARY\n"
            + normalized["summary"]
        )

    if normalized["learning_objectives"]:
        objectives = "\n".join(
            "- " + objective
            for objective in normalized["learning_objectives"]
        )

        sections.append(
            "LEARNING OBJECTIVES\n"
            + objectives
        )

    if normalized["keywords"]:
        keywords = ", ".join(
            normalized["keywords"]
        )

        sections.append(
            "KEYWORDS\n"
            + keywords
        )

    if normalized["concepts"]:
        concepts = "\n".join(
            "- " + concept
            for concept in normalized["concepts"]
        )

        sections.append(
            "CONCEPTS\n"
            + concepts
        )

    if normalized["difficulty"]:
        sections.append(
            "DIFFICULTY\n"
            + normalized["difficulty"]
        )

    return "\n\n".join(sections)


def normalize_for_generation(
    response: Dict[str, Any]
) -> Dict[str, Any]:
    normalized = normalize_content(response)

    return {
        "content": normalized,
        "text": content_to_text(normalized),
    }