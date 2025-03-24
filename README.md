# PDF Knowledge Assistant

This system allows you to ask questions about the contents of a PDF document using a beautiful web interface powered by Streamlit, LangChain, and OpenAI's language models.

![PDF Knowledge Assistant](https://raw.githubusercontent.com/streamlit/streamlit/master/examples/data/logo.png)

## Features

- 📄 Upload any PDF document
- 🔍 Process and analyze the PDF content
- 💬 Ask questions in a chat-like interface
- 🤖 Get AI-powered answers based on the document's content
- 📊 View document statistics
- 🎨 Beautiful, user-friendly interface

## Setup

1. Clone this repository
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Create a `.env` file in the project root directory with your OpenAI API key:
   ```
   OPENAI_API_KEY=your-api-key-here
   ```
   Replace `your-api-key-here` with your actual OpenAI API key.

## Usage

You can use the system in two ways:

### Web Interface (Recommended)

Run the Streamlit app:

```
streamlit run app.py
```

This will:
1. Start a local web server
2. Open a browser window with the PDF Knowledge Assistant
3. Allow you to upload PDFs and ask questions through a friendly interface

### Command Line Interface

Alternatively, you can use the command-line version:

```
python pdf_qa.py path/to/your/document.pdf
```

## How It Works

The system works by:
1. Extracting text from the PDF
2. Splitting the text into manageable chunks
3. Creating vector embeddings for each chunk using OpenAI
4. Using FAISS for similarity search on those embeddings
5. Using LangChain's question-answering chain to generate answers based on relevant text chunks

## Example Questions

Once your PDF is loaded, you can ask questions like:
- "What are the basic human rights mentioned in the document?"
- "What is the highest court in Sri Lanka according to the document?"
- "What are the key findings in this paper?"
- "Summarize the main arguments."
- Any other questions about the content of your PDF 