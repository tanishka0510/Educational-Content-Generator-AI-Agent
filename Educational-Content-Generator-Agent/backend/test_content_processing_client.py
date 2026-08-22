from services.content_processing_client import process_content


response = process_content(
    subject="ETC",
    question="Explain process states",
    document_uploaded=False,
)

print("\n========== RESPONSE ==========\n")
print(response)