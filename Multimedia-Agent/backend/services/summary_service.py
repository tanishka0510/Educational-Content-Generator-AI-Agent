"""
Summary Service

This service generates concise educational summaries
using the configured ChatGroq LLM.
"""

from backend.config import get_llm


class SummaryService:
    """
    Service responsible for generating summaries.
    """

    def __init__(self):
        self.llm = get_llm()

    def generate_summary(self, text: str) -> str:
        """
        Generate a concise educational summary.

        Args:
            text (str): Educational content.

        Returns:
            str: Summary.
        """

        prompt = f"""
You are an educational assistant.

Generate a concise summary of the following educational content.

Rules:
- Preserve important concepts.
- Keep the summary clear.
- Use simple language.
- Do not invent information.

Educational Content:

{text}

Summary:
"""

        response = self.llm.invoke(prompt)

        return response.content.strip()


# ---------------------------------------------------------
# Testing
# ---------------------------------------------------------

if __name__ == "__main__":

    service = SummaryService()

    sample_text = """
Artificial Intelligence is a branch of computer science
that enables machines to mimic human intelligence.
Applications include healthcare, education,
robotics, cybersecurity, and finance.
"""

    summary = service.generate_summary(sample_text)

    print(summary)