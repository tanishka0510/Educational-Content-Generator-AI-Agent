import re

def clean_text(text):
    """
    Clean extracted PDF text.
    """

    # Remove extra spaces
    text = re.sub(r'\s+', ' ', text)

    # Remove repeated blank lines
    text = re.sub(r'\n+', '\n', text)

    # Remove page numbers like "Page 1"
    text = re.sub(r'Page \d+', '', text)

    return text.strip()