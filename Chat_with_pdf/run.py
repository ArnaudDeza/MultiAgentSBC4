"""
Chat with PDF Application

This application allows users to upload PDF documents and ask questions about their content
using Retrieval-Augmented Generation (RAG) with Ollama and LangChain.

The app works by:
1. Loading and splitting PDF documents into chunks
2. Creating vector embeddings for semantic search
3. Retrieving relevant chunks based on user questions
4. Using an LLM to generate answers based on the retrieved context
"""

# Import required libraries
import streamlit as st  # Web framework for creating the user interface

# LangChain imports for document processing and RAG pipeline
from langchain_community.document_loaders import PDFPlumberLoader  # PDF document loader
from langchain_text_splitters import RecursiveCharacterTextSplitter  # Text chunking
from langchain_core.vectorstores import InMemoryVectorStore  # Vector database for embeddings
from langchain_ollama import OllamaEmbeddings  # Ollama embeddings for semantic search
from langchain_core.prompts import ChatPromptTemplate  # Prompt template management
from langchain_ollama.llms import OllamaLLM  # Ollama language model interface

# Define the prompt template for question-answering
# This template structures how the AI should respond to questions using retrieved context
template = """
You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. If you don't know the answer, just say that you don't know. Use three sentences maximum and keep the answer concise.
Question: {question} 
Context: {context} 
Answer:
"""

# Directory where uploaded PDFs will be stored
# Note: You may need to change this path to match your local setup
pdfs_directory = '/storage/home/hcoda1/3/adeza3/p-phentenryck3-1/adeza3/MultiAgentSBC4/Chat_with_pdf/pdfs/'

# Initialize the embedding model for converting text to vectors
# phi4:latest is a powerful model that creates high-quality embeddings for semantic search
embeddings = OllamaEmbeddings(model="phi4:latest")

# Create an in-memory vector store to hold document embeddings
# This allows for fast similarity search when retrieving relevant document chunks
vector_store = InMemoryVectorStore(embeddings)

# Initialize the language model for generating answers
# phi4:latest is used both for embeddings and text generation for consistency
model = OllamaLLM(model="phi4:latest")

def upload_pdf(file):
    """
    Save the uploaded PDF file to the designated directory.
    
    Args:
        file: Streamlit uploaded file object containing the PDF data
    """
    with open(pdfs_directory + file.name, "wb") as f:
        f.write(file.getbuffer())

def load_pdf(file_path):
    """
    Load and extract text content from a PDF file.
    
    Args:
        file_path (str): Path to the PDF file to be loaded
        
    Returns:
        list: List of Document objects containing the extracted text and metadata
    """
    loader = PDFPlumberLoader(file_path)
    documents = loader.load()
    return documents

def split_text(documents):
    """
    Split large documents into smaller, manageable chunks for better retrieval.
    
    This is crucial for RAG systems because:
    - Large documents don't fit well in LLM context windows
    - Smaller chunks improve retrieval accuracy
    - Overlapping chunks ensure context isn't lost at boundaries
    
    Args:
        documents (list): List of Document objects to be split
        
    Returns:
        list: List of smaller Document chunks
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,      # Maximum characters per chunk
        chunk_overlap=200,    # Characters to overlap between chunks
        add_start_index=True  # Track where each chunk came from in the original document
    )
    return text_splitter.split_documents(documents)

def index_docs(documents):
    """
    Add document chunks to the vector store for semantic search.
    
    This process:
    1. Converts each document chunk to a vector embedding
    2. Stores the embedding along with the original text
    3. Enables fast similarity search for question answering
    
    Args:
        documents (list): List of Document chunks to be indexed
    """
    vector_store.add_documents(documents)

def retrieve_docs(query):
    """
    Find the most relevant document chunks for a given query.
    
    Uses semantic similarity search to find chunks that are most likely
    to contain information relevant to the user's question.
    
    Args:
        query (str): User's question or search query
        
    Returns:
        list: List of Document chunks most similar to the query
    """
    return vector_store.similarity_search(query)

def answer_question(question, documents):
    """
    Generate an answer to the user's question using retrieved document context.
    
    This function implements the "Generation" part of RAG:
    1. Combines retrieved document chunks into context
    2. Uses the prompt template to structure the input
    3. Invokes the language model to generate a response
    
    Args:
        question (str): User's question
        documents (list): Retrieved document chunks containing relevant information
        
    Returns:
        str: Generated answer based on the provided context
    """
    # Combine all retrieved document chunks into a single context string
    context = "\n\n".join([doc.page_content for doc in documents])
    
    # Create a prompt using the template
    prompt = ChatPromptTemplate.from_template(template)
    
    # Create a processing chain: prompt -> model
    chain = prompt | model
    
    # Generate and return the answer
    return chain.invoke({"question": question, "context": context})

# === STREAMLIT USER INTERFACE ===

# Create a file uploader widget for PDF files
# This allows users to drag and drop or select PDF files from their computer
uploaded_file = st.file_uploader(
    "Upload PDF",
    type="pdf",                    # Only accept PDF files
    accept_multiple_files=False    # Only allow one file at a time
)

# Process the uploaded file and enable chat functionality
if uploaded_file:
    # Step 1: Save the uploaded file to the server
    upload_pdf(uploaded_file)
    
    # Step 2: Load and extract text from the PDF
    documents = load_pdf(pdfs_directory + uploaded_file.name)
    
    # Step 3: Split the document into smaller chunks for better retrieval
    chunked_documents = split_text(documents)
    
    # Step 4: Create embeddings and store them in the vector database
    # This enables semantic search for relevant content
    index_docs(chunked_documents)
    
    # Create a chat input widget for user questions
    question = st.chat_input()
    
    # Process user questions and generate responses
    if question:
        # Display the user's question in the chat interface
        st.chat_message("user").write(question)
        
        # Step 5: Retrieve relevant document chunks based on the question
        # Uses semantic similarity to find the most relevant content
        related_documents = retrieve_docs(question)
        
        # Step 6: Generate an answer using the retrieved context
        # Combines retrieval with generation (RAG approach)
        answer = answer_question(question, related_documents)
        
        # Display the AI assistant's response in the chat interface
        st.chat_message("assistant").write(answer)

