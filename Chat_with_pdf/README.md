# Chat with PDF Application 📄💬

A powerful Retrieval-Augmented Generation (RAG) application that allows you to upload PDF documents and ask questions about their content using AI. Built with Streamlit, LangChain, and Ollama.

## 🌟 Features

- **PDF Upload**: Drag and drop PDF files directly into the web interface
- **Intelligent Q&A**: Ask questions about your PDF content in natural language
- **Semantic Search**: Uses vector embeddings to find relevant information
- **Real-time Chat**: Interactive chat interface for seamless conversations
- **Local AI**: Runs entirely on your local machine using Ollama models

## 🏗️ How It Works

The application uses a Retrieval-Augmented Generation (RAG) approach:

1. **Document Loading**: Extracts text content from uploaded PDF files
2. **Text Chunking**: Splits large documents into smaller, manageable pieces
3. **Vector Embeddings**: Converts text chunks into numerical vectors for semantic search
4. **Question Processing**: When you ask a question, it finds the most relevant chunks
5. **Answer Generation**: Uses an AI model to generate answers based on retrieved context

## 🛠️ Prerequisites

Before running this application, make sure you have:

### 1. Python Environment
- Python 3.8 or higher
- pip package manager

### 2. Ollama Installation
- Install Ollama from [https://ollama.ai](https://ollama.ai)
- Pull the required model:
  ```bash
  ollama pull phi4:latest
  ```

### 3. System Requirements
- At least 8GB RAM (16GB recommended for larger documents)
- Sufficient disk space for storing PDF files and model data

## 📦 Installation

1. **Clone or download the project**:
   ```bash
   git clone <repository-url>
   cd Chat_with_pdf
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install required packages**:
   ```bash
   pip install streamlit
   pip install langchain-community
   pip install langchain-text-splitters
   pip install langchain-core
   pip install langchain-ollama
   pip install pdfplumber
   ```

   Or install all at once:
   ```bash
   pip install streamlit langchain-community langchain-text-splitters langchain-core langchain-ollama pdfplumber
   ```

4. **Create the PDFs directory**:
   ```bash
   mkdir pdfs
   ```

## ⚙️ Configuration

### Update File Path
Before running the application, you need to update the `pdfs_directory` path in `run.py`:

```python
# Change this line to match your local setup
pdfs_directory = '/path/to/your/Chat_with_pdf/pdfs/'
```

For example:
- **Windows**: `pdfs_directory = 'C:/Users/YourName/Chat_with_pdf/pdfs/'`
- **macOS/Linux**: `pdfs_directory = '/Users/YourName/Chat_with_pdf/pdfs/'`

### Model Configuration
The application uses `phi4:latest` by default. You can change this in `run.py`:

```python
# Change these lines to use a different model
embeddings = OllamaEmbeddings(model="your-preferred-model")
model = OllamaLLM(model="your-preferred-model")
```

## 🚀 Running the Application

1. **Start Ollama** (if not already running):
   ```bash
   ollama serve
   ```

2. **Run the Streamlit application**:
   ```bash
   streamlit run run.py
   ```

3. **Open your browser** and navigate to:
   ```
   http://localhost:8501
   ```

## 📖 Usage Guide

### Step 1: Upload a PDF
- Click on the "Upload PDF" area or drag and drop a PDF file
- Wait for the file to be processed (this may take a moment for large files)

### Step 2: Ask Questions
- Once the PDF is processed, you'll see a chat input at the bottom
- Type your question about the PDF content
- Press Enter to submit

### Step 3: Get Answers
- The AI will analyze your question and search through the PDF
- It will provide an answer based on the relevant content found
- Continue asking follow-up questions as needed

## 💡 Tips for Best Results

### Question Types That Work Well:
- **Factual questions**: "What is the main conclusion of this research?"
- **Specific details**: "What are the requirements mentioned in section 3?"
- **Summaries**: "Can you summarize the key points about X?"
- **Comparisons**: "How does approach A differ from approach B?"

### Question Types to Avoid:
- Questions requiring information not in the PDF
- Very broad questions that would require the entire document
- Questions requiring real-time or updated information

### Document Tips:
- **Text-based PDFs work best** (not scanned images)
- **Smaller files process faster** (under 50 pages recommended)
- **Well-structured documents** with clear headings work better

## 🔧 Troubleshooting

### Common Issues:

1. **"Import could not be resolved" errors**:
   - Make sure all packages are installed: `pip install -r requirements.txt`
   - Check that you're using the correct Python environment

2. **Ollama connection errors**:
   - Ensure Ollama is running: `ollama serve`
   - Verify the model is installed: `ollama list`
   - Check if the model name is correct in the code

3. **File upload issues**:
   - Verify the `pdfs_directory` path exists and is writable
   - Check file permissions
   - Ensure the PDF is not corrupted

4. **Slow performance**:
   - Try smaller PDF files
   - Reduce `chunk_size` in the text splitter
   - Use a faster model if available

5. **Memory issues**:
   - Close other applications
   - Try processing smaller documents
   - Increase system RAM if possible

## 📁 Project Structure

```
Chat_with_pdf/
├── run.py              # Main application file
├── README.md           # This documentation
├── pdfs/              # Directory for uploaded PDF files
└── requirements.txt   # Python dependencies (optional)
```

## 🔒 Privacy & Security

- **Local Processing**: All data stays on your machine
- **No Cloud Services**: No data is sent to external servers
- **Temporary Storage**: PDFs are stored locally in the `pdfs/` directory
- **Session-based**: Vector embeddings are stored in memory and cleared when the app restarts

## 🚀 Advanced Usage

### Customizing the Prompt
You can modify the `template` variable in `run.py` to change how the AI responds:

```python
template = """
Your custom instructions here.
Question: {question} 
Context: {context} 
Answer:
"""
```

### Using Different Models
To use different Ollama models:

1. Install the model: `ollama pull model-name`
2. Update the model names in `run.py`
3. Restart the application

### Batch Processing
For processing multiple PDFs, you can modify the code to accept multiple files and maintain separate vector stores.

## 🤝 Contributing

Feel free to contribute improvements:
- Add support for more file formats
- Implement conversation memory
- Add document metadata display
- Improve error handling
- Add progress indicators

## 📝 License

This project is open source and available under the MIT License.

## 🆘 Support

If you encounter issues:
1. Check this README for troubleshooting steps
2. Verify all prerequisites are installed correctly
3. Test with a small, simple PDF file first
4. Check the Streamlit logs for detailed error messages

---

**Happy chatting with your PDFs! 📄✨** 