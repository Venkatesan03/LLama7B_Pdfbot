import elasticsearch
from elasticsearch import Elasticsearch
import elasticsearch.exceptions
from fastapi import FastAPI, UploadFile, HTTPException, Form, Depends, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from chatBot import ChatBot
from elasticdb import process_pdf_and_create_vector_store
from typing import List
import uvicorn


app = FastAPI()

app.add_middleware(
CORSMiddleware,
allow_origins=["*"],
allow_credentials=True,
allow_methods=["*"],
allow_headers=["*"]
)


class QueryInput(BaseModel):
    query: str

pdfbot = None

# Initialize ChatBot
@app.on_event("startup")
async def startup_event():
    global pdfbot
    pdfbot = create_pdfbot()
    
# Create PDFBot
def create_pdfbot():
    pdfbot_class = ChatBot(index_name=None)
    return pdfbot_class.pdf_bot()

# Initialize PDFBot
@app.post("/initialize_pdfbot")
async def initialize_pdfbot():
    global pdfbot
    pdfbot = create_pdfbot()
    return pdfbot

# Store uploaded PDFs
uploaded_pdfs = []

# Upload PDF files
@app.post("/upload_pdf/")
async def upload_pdf(
    name_for_index: str = Form(...), pdf_files: List[UploadFile] = Form(...)):
    index_name = name_for_index
    if not pdf_files:
        raise HTTPException(status_code=400, detail="No PDF files were uploaded")

    for pdf_file in pdf_files:
        file_content = await pdf_file.read()
        vector_store = process_pdf_and_create_vector_store(file_content, index_name)
        uploaded_pdfs.append({"filename": pdf_file.filename, "vector_store": vector_store})
    return {"message": "PDFs successfully uploaded and processed"}

# Generate AI answer
def genAI_answer(custom_prompt):
    if pdfbot is None:
        raise HTTPException(status_code=500, detail="ChatBot not initialized")

    output_from_llm = pdfbot(custom_prompt)
    answer = output_from_llm['result']
    docs = output_from_llm["source_documents"]

    print(f"\ngenAI_answer completed: \n{answer}\n")
    print(f"\n genAI source docs: {docs}\n")
    return answer

# Ask a question
@app.post("/ask_question/")
async def ask_question(query_input: QueryInput,
                        index_name):
    print(f"index_name  ====  {index_name}\n")
    user_query = query_input.query
    answer = genAI_answer({'query': user_query})

    return {"answer": answer}


# uvicorn.run(app, host="0.0.0.0", port=5000)
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
