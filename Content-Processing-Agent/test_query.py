from app.services.rag_service import ask_question


tests = [
    # ============================================================
    # TEST 1 — Basic local knowledge retrieval
    # ============================================================
    {
        "name": "Basic Local Retrieval",
        "subject": "DBMS",
        "question": "What is normalization?",
        "document_uploaded": False,
        "expected_source": "knowledge_base",
    },

    # ============================================================
    # TEST 2 — Brief explanation
    # ============================================================
    {
        "name": "Brief Explanation",
        "subject": "DBMS",
        "question": "Explain normalization in brief",
        "document_uploaded": False,
        "expected_source": "knowledge_base",
    },

    # ============================================================
    # TEST 3 — Detailed explanation
    # ============================================================
    {
        "name": "Detailed Explanation",
        "subject": "DBMS",
        "question": "Explain normalization in detail",
        "document_uploaded": False,
        "expected_source": "knowledge_base",
    },

    # ============================================================
    # TEST 4 — Beginner/simple language
    # ============================================================
    {
        "name": "Simple Language",
        "subject": "DBMS",
        "question": "Explain normalization in simple language",
        "document_uploaded": False,
        "expected_source": "knowledge_base",
    },

    # ============================================================
    # TEST 5 — Explanation with examples
    # ============================================================
    {
        "name": "Explanation With Examples",
        "subject": "DBMS",
        "question": "Explain normalization with examples",
        "document_uploaded": False,
        "expected_source": "knowledge_base",
    },

    # ============================================================
    # TEST 6 — Local DBMS concept
    # ============================================================
    {
        "name": "Deadlock",
        "subject": "DBMS",
        "question": "Explain deadlock",
        "document_uploaded": False,
        "expected_source": "knowledge_base",
    },

    # ============================================================
    # TEST 7 — Local DBMS concept
    # ============================================================
    {
        "name": "Transaction",
        "subject": "DBMS",
        "question": "What is a transaction?",
        "document_uploaded": False,
        "expected_source": "knowledge_base",
    },

    # ============================================================
    # TEST 8 — Question not properly covered by DBMS KB
    # This should test web fallback.
    # ============================================================
    {
        "name": "Web Fallback",
        "subject": "DBMS",
        "question": "Compare process and thread",
        "document_uploaded": False,
        "expected_source": "web",
    },

    # ============================================================
    # TEST 9 — Another potentially external concept
    # ============================================================
    {
        "name": "External Concept",
        "subject": "DBMS",
        "question": "What is multithreading in operating systems?",
        "document_uploaded": False,
        "expected_source": "web",
    },
]


for index, test in enumerate(tests, start=1):

    print("\n")
    print("=" * 80)
    print(f"TEST {index}: {test['name']}")
    print("=" * 80)

    print("Subject            :", test["subject"])
    print("Question           :", test["question"])
    print("Document Uploaded  :", test["document_uploaded"])
    print("Expected Source    :", test["expected_source"])

    try:

        result = ask_question(
            subject=test["subject"],
            question=test["question"],
            document_uploaded=test["document_uploaded"],
        )

        # ========================================================
        # BASIC RESPONSE
        # ========================================================

        print("\n========== FINAL RAG RESPONSE ==========\n")

        print("Question:")
        print(result.get("question"))

        print("\nAnswer:")
        print(result.get("answer"))

        # ========================================================
        # SOURCE
        # ========================================================

        print("\nSources:")

        sources = result.get("sources", [])

        if sources:
            for source in sources:
                print(" -", source)
        else:
            print(" - No sources")

        # ========================================================
        # RETRIEVAL SCORE
        # ========================================================

        print("\nRetrieval Score:")
        print(result.get("retrieval_score"))

        # ========================================================
        # OPTIONAL RESOURCES
        # ========================================================

        if result.get("videos"):
            print("\nVideos:")
            for video in result["videos"]:
                print(video)

        if result.get("khan"):
            print("\nKhan Academy:")
            for item in result["khan"]:
                print(item)

        if result.get("nptel"):
            print("\nNPTEL:")
            for item in result["nptel"]:
                print(item)

        # ========================================================
        # SOURCE CHECK
        # ========================================================

        print("\n========== TEST VALIDATION ==========")

        actual_source = result.get("source")

        print("Expected Source :", test["expected_source"])
        print("Actual Source   :", actual_source)

        if actual_source:
            if actual_source == test["expected_source"]:
                print("STATUS          : PASS")
            else:
                print("STATUS          : CHECK")
        else:
            print("STATUS          : UNKNOWN")
            print("Reason          : 'source' field not present in response")

        # ========================================================
        # GEMINI CHECK
        # ========================================================

        answer = result.get("answer", "")

        if "language model is unavailable" in answer.lower():

            print("\nLLM STATUS      : UNAVAILABLE")
            print("Reason          : Gemini/API generation failed.")

        else:

            print("\nLLM STATUS      : RESPONSE GENERATED")

        print("\n========================================\n")

    except Exception as e:

        print("\n========== TEST ERROR ==========")
        print("Test:", test["name"])
        print("Error:", e)
        print("================================\n")