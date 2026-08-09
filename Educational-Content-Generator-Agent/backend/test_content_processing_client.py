from services.content_processing_client import process_content

response = process_content(
subject="OOP",
question="What is inheritance",
document_uploaded=False,
)

print("\n========== RESPONSE ==========\n")

print(response)
