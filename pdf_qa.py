import os
import sys
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain_openai import OpenAI

# Load environment variables from .env file
load_dotenv()

# Get API key from environment
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("Error: OPENAI_API_KEY not found in .env file")
    sys.exit(1)
print("API key is loaded successfully")

def read_pdf(pdf_path):
    """Extract text from a PDF file"""
    pdf_reader = PdfReader(pdf_path)
    raw_text = ''
    for page in pdf_reader.pages:
        content = page.extract_text()
        if content:
            raw_text += content
    return raw_text

def split_text(raw_text):
    """Split text into manageable chunks"""
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=900,
        chunk_overlap=200,
        length_function=len,
    )
    return text_splitter.split_text(raw_text)

def create_vector_store(texts):
    """Create a FAISS vector store from text chunks"""
    embeddings = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))
    return FAISS.from_texts(texts, embeddings)

def answer_question(vector_store, question):
    """Answer a question using the PDF content"""
    chain = load_qa_chain(OpenAI(openai_api_key=os.getenv("OPENAI_API_KEY")), chain_type="stuff")
    docs = vector_store.similarity_search(question)
    return chain.run(input_documents=docs, question=question)

def main():
    # Check if PDF path is provided
    if len(sys.argv) < 2:
        print("Usage: python pdf_qa.py <path_to_pdf>")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    
    # Process the PDF
    print(f"Reading PDF: {pdf_path}")
    raw_text = read_pdf(pdf_path)
    print(f"Extracted {len(raw_text)} characters from PDF")
    
    texts = split_text(raw_text)
    print(f"Split into {len(texts)} text chunks")
    
    vector_store = create_vector_store(texts)
    print("Vector store created successfully")
    
    # Interactive Q&A loop
    print("\nYou can now ask questions about the PDF content. Type 'exit' to quit.")
    while True:
        question = input("\nYour question: ")
        if question.lower() == 'exit':
            break
        
        try:
            answer = answer_question(vector_store, question)
            print(f"\nAnswer: {answer}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main() 