import fitz  # PyMuPDF
import json

def extract_llm_context(pdf_path):
    doc = fitz.open(pdf_path)
    extracted_data = []

    for page in doc:
        for annot in page.annots():
            info = annot.info
            content = info.get("content")  # The actual comment text
            author = info.get("title", "Unknown")
            
            if content:
                # Extract text physically located under the annotation bounding box
                rect = annot.rect
                source_text = page.get_text("text", clip=rect).strip()
                
                extracted_data.append({
                    "page": page.number + 1,
                    "author": author,
                    "referenced_text": source_text if source_text else "N/A (Sticky Note)",
                    "comment": content
                })
                
    return extracted_data

# Generate clean JSON context for your LLM prompt
pdf_context = extract_llm_context("C:\\Users\\sashi\\Documents\\Wits work\\honors\\Research methods intro\\Research proposal\\research proposal 2459211 comments.pdf")
print(json.dumps(pdf_context, indent=2))