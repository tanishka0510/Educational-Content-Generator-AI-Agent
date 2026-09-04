import json
import re
import requests

from quiz.schemas import (
    QuizGenerateRequest,
    QuizGenerateResponse,
    QuizQuestionResponse,
)

from services.gemini_service import ask_gemini
from prompts.quiz_prompt import create_quiz_prompt

# ============================================================
# CONTENT PROCESSING AGENT
# ============================================================

CONTENT_PROCESSING_AGENT_URL = (
    "http://127.0.0.1:8001"
)

QUIZ_RETRIEVAL_ENDPOINT = (
    f"{CONTENT_PROCESSING_AGENT_URL}/quiz/retrieve"
)


# ============================================================
# Build Context From Retrieved Documents
# ============================================================

def _build_context(
    documents,
    external_context="",
):
    """
    Convert retrieved documents into a single text context
    that can be passed to Gemini.
    """

    context_parts = []

    # --------------------------------------------------------
    # Retrieved documents
    # --------------------------------------------------------

    if documents:

        for document in documents:

            # LangChain Document object
            if hasattr(
                document,
                "page_content",
            ):

                content = document.page_content

            # Dictionary returned by API
            elif isinstance(
                document,
                dict,
            ):

                content = (
                    document.get("page_content")
                    or document.get("content")
                    or ""
                )

            # Plain string
            elif isinstance(
                document,
                str,
            ):

                content = document

            else:

                content = ""

            if content and content.strip():

                context_parts.append(
                    content.strip()
                )

    # --------------------------------------------------------
    # External context
    # --------------------------------------------------------

    if (
        isinstance(
            external_context,
            str,
        )
        and external_context.strip()
    ):

        context_parts.append(
            external_context.strip()
        )

    return "\n\n".join(
        context_parts
    )


# ============================================================
# Parse Gemini JSON
# ============================================================

def _parse_json(text: str):
    """
    Parse JSON returned by Gemini.

    Handles both:

        {...}

    and:

        ```json
        {...}
        ```
    """

    if not text:

        raise ValueError(
            "Gemini returned an empty response."
        )

    text = text.strip()

    # --------------------------------------------------------
    # Remove markdown code fences
    # --------------------------------------------------------

    if text.startswith("```"):

        text = re.sub(
            r"^```(?:json)?",
            "",
            text,
            flags=re.IGNORECASE,
        )

        text = re.sub(
            r"```$",
            "",
            text,
        ).strip()

    # --------------------------------------------------------
    # Extract JSON object
    # --------------------------------------------------------

    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end == -1:

        raise ValueError(
            "Gemini response does not contain "
            "a valid JSON object."
        )

    json_text = text[
        start:end + 1
    ]

    # --------------------------------------------------------
    # Parse JSON
    # --------------------------------------------------------

    try:

        return json.loads(
            json_text
        )

    except json.JSONDecodeError as e:

        raise ValueError(
            f"Failed to parse Gemini JSON response: {e}"
        )


# ============================================================
# Retrieve Quiz Content
# ============================================================

def _retrieve_quiz_content(
    request: QuizGenerateRequest,
):
    """
    Request relevant study material from the
    Content Processing Agent.

    The Educational Content Generator does NOT directly
    import hybrid_retriever or quiz_retrieval.

    Communication between the two agents happens through
    HTTP.
    """

    payload = {

        "subject": request.subject,

        "unit": request.unit,

        "topic": request.topic,

        "difficulty": request.difficulty,

        "number_of_questions": (
            request.number_of_questions
        ),

        "document_uploaded": (
            request.document_uploaded
        ),
    }

    print(
        "\n=========================================="
    )

    print(
        "       QUIZ CONTENT RETRIEVAL"
    )

    print(
        "=========================================="
    )

    print(
        "Retrieval Endpoint :",
        QUIZ_RETRIEVAL_ENDPOINT,
    )

    print(
        "Subject            :",
        request.subject,
    )

    print(
        "Unit               :",
        request.unit,
    )

    print(
        "Topic              :",
        request.topic,
    )

    print(
        "Difficulty         :",
        request.difficulty,
    )

    print(
        "Questions          :",
        request.number_of_questions,
    )

    print(
        "Document Uploaded  :",
        request.document_uploaded,
    )

    # ========================================================
    # HTTP REQUEST
    # ========================================================

    try:

        response = requests.post(

            QUIZ_RETRIEVAL_ENDPOINT,

            json=payload,

            timeout=60,
        )

    except requests.RequestException as e:

        print(
            "\nQuiz Retrieval Error:",
            e,
        )

        raise ValueError(
            "Could not connect to the "
            "Content Processing Agent."
        ) from e

    # ========================================================
    # CHECK RESPONSE
    # ========================================================

    print(
        "\nRetrieval Status Code :",
        response.status_code,
    )

    if response.status_code != 200:

        try:

            error_detail = (
                response.json()
            )

        except Exception:

            error_detail = response.text

        print(
            "Retrieval Error Response :",
            error_detail,
        )

        raise ValueError(
            "Quiz retrieval failed: "
            f"{error_detail}"
        )

    # ========================================================
    # PARSE RESPONSE
    # ========================================================

    try:

        retrieval = response.json()

    except ValueError as e:

        raise ValueError(
            "Content Processing Agent returned "
            "invalid JSON."
        ) from e

    print(
        "\nQuiz retrieval completed."
    )

    return retrieval


# ============================================================
# Validate Retrieved Content
# ============================================================

def _validate_retrieval(
    retrieval,
):
    """
    Validate the response received from the
    Content Processing Agent.
    """

    if not isinstance(
        retrieval,
        dict,
    ):

        raise ValueError(
            "Invalid quiz retrieval response."
        )

    documents = retrieval.get(
        "documents",
        [],
    )

    external_context = retrieval.get(
        "external_context",
        "",
    )

    return (
        documents,
        external_context,
    )


# ============================================================
# Generate Quiz
# ============================================================

def generate_quiz(
    request: QuizGenerateRequest,
) -> QuizGenerateResponse:

    # ========================================================
    # STEP 1
    # Retrieve relevant study material
    # ========================================================

    retrieval = _retrieve_quiz_content(
        request
    )

    (
        documents,
        external_context,
    ) = _validate_retrieval(
        retrieval
    )

    # ========================================================
    # STEP 2
    # Build LLM context
    # ========================================================

    context = _build_context(

        documents=documents,

        external_context=external_context,
    )

    print(
        "\n========== QUIZ CONTEXT =========="
    )

    print(
        "Documents Retrieved :",
        len(documents),
    )

    print(
        "Context Length      :",
        len(context),
    )

    print(
        "=================================="
    )

    # --------------------------------------------------------
    # No context
    # --------------------------------------------------------

    if not context.strip():

        raise ValueError(
            "No sufficient content found "
            "for quiz generation."
        )

    # ========================================================
    # STEP 3
    # Build Gemini prompt
    # ========================================================

    # ========================================================
    # STEP 3
    # Build Gemini prompt
    # ========================================================

    prompt = create_quiz_prompt(
        text=context,
        subject=request.subject,
        unit=request.unit,
        topic=request.topic,
        difficulty=request.difficulty,
        number_of_questions=request.number_of_questions,
    )

    print("\n========== QUIZ PROMPT CREATED ==========")
    print("Prompt Length :", len(prompt))
    print("==========================================")

    # ========================================================
    # STEP 4
    # Call Gemini
    # ========================================================

    print("\n========== GEMINI QUIZ GENERATION ==========")
    response_text = ask_gemini(prompt)
    if not response_text:
        raise ValueError(
            "Gemini returned an empty response."
        )
    print(
        "Gemini response received."
    )

    # ========================================================
    # STEP 5
    # Parse Gemini JSON
    # ========================================================

    parsed = _parse_json(
        response_text
    )

    # ========================================================
    # STEP 6
    # Validate JSON structure
    # ========================================================

    if not isinstance(
        parsed,
        dict,
    ):

        raise ValueError(
            "Gemini returned an invalid quiz structure."
        )

    generated_questions = (
        parsed.get(
            "questions",
            [],
        )
    )

    if not isinstance(
        generated_questions,
        list,
    ):

        raise ValueError(
            "Gemini returned an invalid questions list."
        )

    # ========================================================
    # STEP 7
    # Validate Question Count
    # ========================================================

    if len(
        generated_questions
    ) != request.number_of_questions:

        raise ValueError(
            "Gemini generated "
            f"{len(generated_questions)} questions "
            "instead of "
            f"{request.number_of_questions}."
        )

    # ========================================================
    # STEP 8
    # Convert Questions To Schema
    # ========================================================

    questions = []

    for index, item in enumerate(
        generated_questions,
        start=1,
    ):

        if not isinstance(
            item,
            dict,
        ):

            raise ValueError(
                f"Question {index} has an invalid structure."
            )

        question = item.get(
            "question",
            "",
        )

        options = item.get(
            "options",
            [],
        )

        correct_answer = item.get(
            "correct_answer",
            "",
        )

        explanation = item.get(
            "explanation",
            "",
        )

        # ----------------------------------------------------
        # Validate question
        # ----------------------------------------------------

        if not question.strip():

            raise ValueError(
                f"Question {index} is empty."
            )

        # ----------------------------------------------------
        # Validate options
        # ----------------------------------------------------

        if not isinstance(
            options,
            list,
        ):

            raise ValueError(
                f"Question {index} options must be a list."
            )

        if len(options) != 4:

            raise ValueError(
                f"Question {index} must contain "
                "exactly 4 options."
            )

        # ----------------------------------------------------
        # Validate correct answer
        # ----------------------------------------------------

        if correct_answer not in options:

            raise ValueError(
                f"Question {index} correct_answer "
                "does not match any option."
            )

        # ----------------------------------------------------
        # Validate explanation
        # ----------------------------------------------------

        if not explanation.strip():

            raise ValueError(
                f"Question {index} has no explanation."
            )

        # ----------------------------------------------------
        # Create schema object
        # ----------------------------------------------------

        questions.append(

            QuizQuestionResponse(

                id=index,

                question=question,

                options=options,

                correct_answer=correct_answer,

                explanation=explanation,

                topic=request.topic,

                difficulty=request.difficulty,
            )
        )

    # ========================================================
    # STEP 9
    # Build Final Response
    # ========================================================

    quiz_title = parsed.get(
        "quiz_title",
        "",
    )

    if not quiz_title.strip():

        quiz_title = (
            f"{request.subject} "
            f"{request.difficulty.title()} Quiz"
        )

    result = QuizGenerateResponse(

        quiz_title=quiz_title,

        subject=request.subject,

        unit=request.unit,

        topic=request.topic,

        difficulty=request.difficulty,

        questions=questions,

        total_questions=len(
            questions
        ),
    )

    print(
        "\n========== QUIZ GENERATION COMPLETE =========="
    )

    print(
        "Quiz Title        :",
        result.quiz_title,
    )

    print(
        "Subject           :",
        result.subject,
    )

    print(
        "Unit              :",
        result.unit,
    )

    print(
        "Topic             :",
        result.topic,
    )

    print(
        "Difficulty        :",
        result.difficulty,
    )

    print(
        "Questions         :",
        result.total_questions,
    )

    print(
        "==============================================="
    )

    return result