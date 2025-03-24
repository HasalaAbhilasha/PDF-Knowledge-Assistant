import os
import tempfile
import streamlit as st
import json
import base64
import shutil
from datetime import datetime
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain_openai import OpenAI
from logo import get_logo_html
from pdfutils import find_page_and_highlight, get_pdf_download_link, cleanup_temp_pdf

# Load environment variables
load_dotenv()

# Page config
st.set_page_config(
    page_title="PDF Knowledge Assistant",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize theme settings
if 'theme' not in st.session_state:
    st.session_state.theme = 'light'

# Theme toggle function
def toggle_theme():
    st.session_state.theme = 'dark' if st.session_state.theme == 'light' else 'light'

# Custom CSS
def get_custom_css(theme):
    if theme == 'dark':
        return """
        <style>
            .main {
                background-color: #0e1117;
                color: #fafafa;
            }
            .stApp {
                max-width: 1200px;
                margin: 0 auto;
                background-color: #0e1117;
                color: #fafafa;
            }
            .css-18e3th9 {
                padding-top: 2rem;
            }
            .stButton button {
                background-color: #4f8bf9;
                color: white;
                border-radius: 5px;
                padding: 0.5rem 1rem;
                font-weight: bold;
            }
            .stButton button:hover {
                background-color: #3a7be6;
            }
            .chat-message {
                padding: 1rem;
                border-radius: 0.5rem;
                margin-bottom: 1rem;
                display: flex;
                align-items: flex-start;
            }
            .chat-message.user {
                background-color: #1c2535;
                border: 1px solid #2d3748;
            }
            .chat-message.assistant {
                background-color: #262730;
                border: 1px solid #2d3748;
            }
            .chat-message .avatar {
                width: 40px;
                height: 40px;
                border-radius: 50%;
                margin-right: 1rem;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 1.2rem;
            }
            .chat-message .user-avatar {
                background-color: #4f8bf9;
                color: white;
            }
            .chat-message .assistant-avatar {
                background-color: #ef4da0;
                color: white;
            }
            .chat-message .content {
                width: 80%;
                color: #fafafa;
            }
            h1, h2, h3 {
                color: #4f8bf9;
            }
            .pdf-info {
                background-color: #262730;
                padding: 1rem;
                border-radius: 0.5rem;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
                margin-bottom: 1rem;
                color: #fafafa;
                border: 1px solid #2d3748;
            }
            .stProgress .st-bo {
                background-color: #4f8bf9;
            }
            .info-card {
                background-color: #262730;
                padding: 1.5rem;
                border-radius: 0.5rem;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
                height: 100%;
                color: #fafafa;
                border: 1px solid #2d3748;
            }
            .stTextInput > div {
                background-color: #262730;
                color: #fafafa;
                border-radius: 0.5rem;
                border: 1px solid #2d3748;
            }
            .stTextInput input {
                color: #fafafa;
            }
            .sidebar .sidebar-content {
                background-color: #0e1117;
            }
            .stMarkdown {
                color: #fafafa;
            }
            .stSelectbox > div {
                background-color: #262730;
                color: #fafafa;
                border-radius: 0.5rem;
                border: 1px solid #2d3748;
            }
            .stSelectbox select {
                color: #fafafa;
            }
            .stFileUploader > div {
                background-color: #262730;
                color: #fafafa;
                border-radius: 0.5rem;
                border: 1px solid #2d3748;
            }
        </style>
        """
    else:
        return """
        <style>
            .main {
                background-color: #f5f7f9;
            }
            .stApp {
                max-width: 1200px;
                margin: 0 auto;
                background-color: #f5f7f9;
            }
            .css-18e3th9 {
                padding-top: 2rem;
            }
            .stButton button {
                background-color: #4f8bf9;
                color: white;
                border-radius: 5px;
                padding: 0.5rem 1rem;
                font-weight: bold;
            }
            .stButton button:hover {
                background-color: #3a7be6;
            }
            .chat-message {
                padding: 1rem;
                border-radius: 0.5rem;
                margin-bottom: 1rem;
                display: flex;
                align-items: flex-start;
            }
            .chat-message.user {
                background-color: #e6f3ff;
                border: 1px solid #cbd5e0;
            }
            .chat-message.assistant {
                background-color: #f0f2f6;
                border: 1px solid #cbd5e0;
            }
            .chat-message .avatar {
                width: 40px;
                height: 40px;
                border-radius: 50%;
                margin-right: 1rem;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 1.2rem;
            }
            .chat-message .user-avatar {
                background-color: #4f8bf9;
                color: white;
            }
            .chat-message .assistant-avatar {
                background-color: #ef4da0;
                color: white;
            }
            .chat-message .content {
                width: 80%;
                color: #1a202c;
            }
            h1, h2, h3 {
                color: #1e3a8a;
            }
            .pdf-info {
                background-color: white;
                padding: 1rem;
                border-radius: 0.5rem;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
                margin-bottom: 1rem;
                border: 1px solid #cbd5e0;
            }
            .stProgress .st-bo {
                background-color: #4f8bf9;
            }
            .info-card {
                background-color: white;
                padding: 1.5rem;
                border-radius: 0.5rem;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
                height: 100%;
                border: 1px solid #cbd5e0;
            }
            .stTextInput > div {
                background-color: white;
                color: #1a202c;
                border-radius: 0.5rem;
                border: 1px solid #cbd5e0;
            }
            .stTextInput input {
                color: #1a202c;
            }
            .stMarkdown {
                color: #1a202c;
            }
            .stSelectbox > div {
                background-color: white;
                color: #1a202c;
                border-radius: 0.5rem;
                border: 1px solid #cbd5e0;
            }
            .stSelectbox select {
                color: #1a202c;
            }
            .stFileUploader > div {
                background-color: white;
                color: #1a202c;
                border-radius: 0.5rem;
                border: 1px solid #cbd5e0;
            }
        </style>
        """

# Apply theme CSS
st.markdown(get_custom_css(st.session_state.theme), unsafe_allow_html=True)

# Initialize session state variables
if 'vector_store' not in st.session_state:
    st.session_state.vector_store = None
if 'file_processed' not in st.session_state:
    st.session_state.file_processed = False
if 'pdf_name' not in st.session_state:
    st.session_state.pdf_name = ""
if 'page_count' not in st.session_state:
    st.session_state.page_count = 0
if 'char_count' not in st.session_state:
    st.session_state.char_count = 0
if 'text_chunks' not in st.session_state:
    st.session_state.text_chunks = 0
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'feedback' not in st.session_state:
    st.session_state.feedback = {}
if 'pdf_path' not in st.session_state:
    st.session_state.pdf_path = None
if 'highlighted_pdfs' not in st.session_state:
    st.session_state.highlighted_pdfs = {}
if 'pdf_data' not in st.session_state:
    st.session_state.pdf_data = None

# Check for API key
api_key = os.getenv("OPENAI_API_KEY")
if api_key == "your-api-key-here":
    st.error("⚠️ OpenAI API key is not set. Please update your .env file with your API key.")
    st.stop()

def read_pdf(pdf_file):
    """Extract text from a PDF file"""
    pdf_reader = PdfReader(pdf_file)
    st.session_state.page_count = len(pdf_reader.pages)
    
    raw_text = ''
    for page in pdf_reader.pages:
        content = page.extract_text()
        if content:
            raw_text += content
    
    st.session_state.char_count = len(raw_text)
    return raw_text

def split_text(raw_text):
    """Split text into manageable chunks"""
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=900,
        chunk_overlap=200,
        length_function=len,
    )
    texts = text_splitter.split_text(raw_text)
    st.session_state.text_chunks = len(texts)
    return texts

def create_vector_store(texts):
    """Create a FAISS vector store from text chunks"""
    embeddings = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))
    return FAISS.from_texts(texts, embeddings)

def answer_question(vector_store, question):
    """Answer a question using the PDF content"""
    chain = load_qa_chain(OpenAI(openai_api_key=os.getenv("OPENAI_API_KEY")), chain_type="stuff")
    docs = vector_store.similarity_search(question)
    answer = chain.run(input_documents=docs, question=question)
    
    # Clean up previous highlighted PDFs
    if question in st.session_state.highlighted_pdfs and os.path.exists(st.session_state.highlighted_pdfs[question]):
        cleanup_temp_pdf(st.session_state.highlighted_pdfs[question])
    
    # Generate highlighted PDF for reference
    if st.session_state.pdf_path and os.path.exists(st.session_state.pdf_path):
        try:
            highlighted_pdf, pages = find_page_and_highlight(st.session_state.pdf_path, answer)
            if highlighted_pdf and os.path.exists(highlighted_pdf):
                st.session_state.highlighted_pdfs[question] = highlighted_pdf
                return answer, highlighted_pdf, pages
        except Exception as e:
            st.warning(f"Could not highlight PDF: {e}")
    
    return answer, None, []

def display_chat_history():
    """Display the chat history in a nice format"""
    for i, message in enumerate(st.session_state.chat_history):
        if message["role"] == "user":
            st.markdown(f"""
            <div class="chat-message user">
                <div class="avatar user-avatar">👤</div>
                <div class="content">
                    <p><strong>You:</strong> {message["content"]}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="chat-message assistant">
                <div class="avatar assistant-avatar">🤖</div>
                <div class="content">
                    <p><strong>Assistant:</strong> {message["content"]["answer"]}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Display PDF highlight link if available
            if "highlighted_pdf" in message["content"] and message["content"]["highlighted_pdf"] and os.path.exists(message["content"]["highlighted_pdf"]):
                st.markdown(
                    get_pdf_download_link(
                        message["content"]["highlighted_pdf"], 
                        f"highlighted_{i}.pdf"
                    ),
                    unsafe_allow_html=True
                )
                if "pages" in message["content"] and message["content"]["pages"]:
                    st.info(f'Found on page(s): {", ".join(str(p+1) for p in message["content"]["pages"])}')
            
            # Add feedback buttons under each AI response
            if i not in st.session_state.feedback:
                col1, col2, col3 = st.columns([1, 1, 10])
                with col1:
                    if st.button("👍", key=f"thumbs_up_{i}"):
                        st.session_state.feedback[i] = "positive"
                        st.rerun()
                with col2:
                    if st.button("👎", key=f"thumbs_down_{i}"):
                        st.session_state.feedback[i] = "negative"
                        st.rerun()
            else:
                if st.session_state.feedback[i] == "positive":
                    st.success("Thank you for your positive feedback!")
                else:
                    st.error("Thank you for your feedback. We'll work to improve our responses.")

def process_pdf(uploaded_file):
    """Process an uploaded PDF file"""
    with st.spinner("Processing PDF, please wait..."):
        # Create a permanent file in the app directory
        os.makedirs("temp_pdfs", exist_ok=True)
        pdf_path = os.path.join("temp_pdfs", uploaded_file.name)
        
        # Save the uploaded file
        with open(pdf_path, "wb") as f:
            f.write(uploaded_file.getvalue())
        
        st.session_state.pdf_name = uploaded_file.name
        st.session_state.pdf_path = pdf_path
        st.session_state.pdf_data = uploaded_file.getvalue()  # Store the PDF data in session state
        
        # Process PDF
        progress_bar = st.progress(0)
        
        # Read PDF
        raw_text = read_pdf(pdf_path)
        progress_bar.progress(33)
        
        # Split text
        texts = split_text(raw_text)
        progress_bar.progress(66)
        
        # Create vector store
        st.session_state.vector_store = create_vector_store(texts)
        progress_bar.progress(100)
        
        st.session_state.file_processed = True
    
    st.success("PDF processed successfully! You can now ask questions.")

def export_chat_history():
    """Generate a downloadable file with chat history"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"chat_history_{timestamp}.json"
    
    # Create a simplified version of chat history for export
    simplified_history = []
    for message in st.session_state.chat_history:
        if message["role"] == "user":
            simplified_history.append({
                "role": "user",
                "content": message["content"]
            })
        else:
            simplified_history.append({
                "role": "assistant",
                "content": message["content"]["answer"]
            })
    
    # Create JSON with chat history and PDF info
    export_data = {
        "pdf_name": st.session_state.pdf_name,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "chat_history": simplified_history
    }
    
    # Convert to JSON string
    json_str = json.dumps(export_data, indent=2)
    
    # Create a download link
    b64 = base64.b64encode(json_str.encode()).decode()
    href = f'<a href="data:application/json;base64,{b64}" download="{filename}">Download Chat History</a>'
    return href

# Sidebar
with st.sidebar:
    st.markdown(get_logo_html(), unsafe_allow_html=True)
    st.title("PDF Knowledge Assistant")
    st.markdown("---")
    
    # Theme toggle
    if st.button("🌙 Dark Mode" if st.session_state.theme == 'light' else "☀️ Light Mode", use_container_width=True):
        toggle_theme()
        st.rerun()
    
    st.markdown("---")
    
    st.subheader("Upload your PDF")
    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
    
    if uploaded_file is not None and not st.session_state.file_processed:
        if st.button("Process PDF"):
            process_pdf(uploaded_file)
    
    if st.session_state.file_processed:
        st.markdown("---")
        st.subheader("PDF Information")
        st.markdown(f"""
        <div class="pdf-info">
            <p><strong>File:</strong> {st.session_state.pdf_name}</p>
            <p><strong>Pages:</strong> {st.session_state.page_count}</p>
            <p><strong>Characters:</strong> {st.session_state.char_count:,}</p>
            <p><strong>Text chunks:</strong> {st.session_state.text_chunks}</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Process New PDF"):
            # Clean up any temporary files
            if st.session_state.pdf_path and os.path.exists(st.session_state.pdf_path):
                try:
                    os.remove(st.session_state.pdf_path)
                except:
                    pass
            
            for pdf_path in st.session_state.highlighted_pdfs.values():
                if pdf_path and os.path.exists(pdf_path):
                    try:
                        os.remove(pdf_path)
                    except:
                        pass
            
            st.session_state.vector_store = None
            st.session_state.file_processed = False
            st.session_state.pdf_name = ""
            st.session_state.page_count = 0
            st.session_state.char_count = 0
            st.session_state.text_chunks = 0
            st.session_state.chat_history = []
            st.session_state.feedback = {}
            st.session_state.pdf_path = None
            st.session_state.highlighted_pdfs = {}
            st.session_state.pdf_data = None
            st.rerun()
    
    st.markdown("---")
    st.caption("Made with ❤️ using Streamlit and LangChain")

# Main content
if not st.session_state.file_processed:
    st.title("📚 PDF Knowledge Assistant")
    st.markdown("""
    ### Welcome to PDF Knowledge Assistant!
    
    This app allows you to extract knowledge from any PDF document and ask questions about its contents.
    
    **To get started:**
    1. Upload a PDF file using the sidebar
    2. Click "Process PDF" to analyze the document
    3. Ask questions about the PDF content
    
    The system will use AI to find the most relevant information and provide accurate answers.
    """)
    
    # Display example cards
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="info-card">
            <h3>Example Questions</h3>
            <ul>
                <li>"What are the key findings in this paper?"</li>
                <li>"Summarize the main arguments."</li>
                <li>"What methodology was used in the research?"</li>
                <li>"What are the limitations mentioned?"</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="info-card">
            <h3>How It Works</h3>
            <ol>
                <li>Your PDF is split into smaller chunks</li>
                <li>AI creates semantic embeddings of each chunk</li>
                <li>When you ask a question, the system finds the most relevant chunks</li>
                <li>The AI generates an answer based on those chunks</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)

else:
    st.title(f"Chat with your PDF: {st.session_state.pdf_name}")
    
    # Display chat interface
    display_chat_history()
    
    # Question input with a "Send" button
    with st.form(key="question_form", clear_on_submit=True):
        col1, col2 = st.columns([5, 1])
        with col1:
            user_question = st.text_input("Ask a question about your PDF:", key="question_input")
        with col2:
            submit_button = st.form_submit_button("Send")
        
        if submit_button and user_question:
            # Add user question to chat history
            st.session_state.chat_history.append({"role": "user", "content": user_question})
            
            # Get answer
            with st.spinner("Thinking..."):
                try:
                    answer, highlighted_pdf, pages = answer_question(st.session_state.vector_store, user_question)
                    # Add assistant answer to chat history
                    st.session_state.chat_history.append({
                        "role": "assistant", 
                        "content": {
                            "answer": answer,
                            "highlighted_pdf": highlighted_pdf,
                            "pages": pages
                        }
                    })
                except Exception as e:
                    st.error(f"Error: {e}")
            
            # Rerun to update the display
            st.rerun()
    
    # Add export and clear buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.session_state.chat_history and st.button("Clear Chat History"):
            st.session_state.chat_history = []
            st.session_state.feedback = {}
            st.rerun()
    
    with col2:
        if st.session_state.chat_history:
            st.markdown(export_chat_history(), unsafe_allow_html=True)

# Cleanup temporary files when the app stops
def cleanup_temp_files():
    temp_dir = "temp_pdfs"
    if os.path.exists(temp_dir):
        try:
            shutil.rmtree(temp_dir)
        except:
            pass

# Register the cleanup function to run on session end
import atexit
atexit.register(cleanup_temp_files) 