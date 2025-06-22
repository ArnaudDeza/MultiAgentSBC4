# Import necessary libraries for building a RAG (Retrieval-Augmented Generation) system
import streamlit as st  # Web app framework for creating the user interface

# LangChain imports for document processing and RAG functionality
from langchain_community.document_loaders import PDFPlumberLoader  # For loading PDF documents
from langchain_text_splitters import RecursiveCharacterTextSplitter  # For splitting documents into chunks
from langchain_core.vectorstores import InMemoryVectorStore  # For storing document embeddings in memory
from langchain_ollama import OllamaEmbeddings  # For creating embeddings using Ollama models
from langchain_core.prompts import ChatPromptTemplate  # For creating structured prompts
from langchain_ollama.llms import OllamaLLM  # For using Ollama language models
from langchain_community.retrievers import BM25Retriever  # For keyword-based document retrieval
from nltk.tokenize import word_tokenize  # For tokenizing text (splitting into words)
from langchain.retrievers import EnsembleRetriever  # For combining multiple retrieval methods

# Define the prompt template that will be used to generate answers
# This template provides context and instructions for the AI model
template = """
You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. If you don't know the answer, just say that you don't know. Use three sentences maximum and keep the answer concise.
Question: {question} 
Context: {context} 
Answer:
"""

# Directory path where uploaded PDF files will be stored
# Note: This path appears to be specific to a particular system/environment
pdfs_directory = '/storage/home/hcoda1/3/adeza3/p-phentenryck3-1/adeza3/MultiAgentSBC4/Rag/pdfs/'

# Initialize the Ollama language model
# Using phi4:latest model for generating responses (different from MultiModalRag which uses deepseek)
model = OllamaLLM(model="phi4:latest")

def upload_pdf(file):
    """
    Save the uploaded PDF file to the designated directory.
    
    Args:
        file: Streamlit uploaded file object containing the PDF data
    """
    # Write the uploaded file's buffer content to a file in the pdfs directory
    with open(pdfs_directory + file.name, "wb") as f:
        f.write(file.getbuffer())

def load_pdf(file_path):
    """
    Load and parse a PDF document from the given file path.
    
    Uses PDFPlumberLoader which is excellent for extracting text from PDFs
    while preserving structure and handling complex layouts.
    
    Args:
        file_path (str): Path to the PDF file to be loaded
        
    Returns:
        list: List of document objects containing the PDF content
    """
    # Use PDFPlumberLoader to extract text and structure from PDF
    loader = PDFPlumberLoader(file_path)
    documents = loader.load()

    return documents

def split_text(documents):
    """
    Split large documents into smaller, manageable chunks for better retrieval.
    
    Document chunking is crucial for RAG systems because:
    1. Large documents may exceed model context limits
    2. Smaller chunks allow for more precise retrieval
    3. Overlapping chunks ensure context isn't lost at boundaries
    4. Better chunks lead to more relevant retrievals
    
    Args:
        documents (list): List of document objects to be split
        
    Returns:
        list: List of smaller document chunks with metadata
    """
    # Configure the text splitter with specific parameters
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,        # Maximum size of each chunk (in characters)
        chunk_overlap=200,      # Overlap between chunks to maintain context
        add_start_index=True    # Add metadata about where each chunk starts in original document
    )

    return text_splitter.split_documents(documents)

def build_semantic_retriever(documents):
    """
    Create a semantic retriever that finds documents based on meaning and context.
    
    Semantic retrieval uses embeddings (vector representations) to find
    documents that are conceptually similar to the query, even if they
    don't share exact keywords. This is powerful for understanding intent
    and finding relevant information based on meaning rather than just words.
    
    Args:
        documents (list): List of document chunks to index
        
    Returns:
        Retriever: A semantic retriever object that can find similar documents
    """
    # Create embeddings using the same model for consistency
    # phi4:latest is used here to match the language model
    embeddings = OllamaEmbeddings(model="phi4:latest")
    
    # Create an in-memory vector store to hold the document embeddings
    # This stores the vector representations of all document chunks
    vector_store = InMemoryVectorStore(embeddings)
    
    # Add all documents to the vector store (this creates embeddings for each chunk)
    # This is where the actual vectorization happens
    vector_store.add_documents(documents)

    # Return a retriever interface to the vector store
    # This allows us to search for similar documents using queries
    return vector_store.as_retriever()

def build_bm25_retriever(documents):
    """
    Create a BM25 retriever that finds documents based on keyword matching.
    
    BM25 (Best Matching 25) is a traditional information retrieval algorithm that:
    1. Looks for exact keyword matches between query and documents
    2. Considers term frequency (how often a word appears in a document)
    3. Considers document frequency (how rare a word is across all documents)
    4. Works exceptionally well for specific terms, proper nouns, and technical terms
    
    Args:
        documents (list): List of document chunks to index
        
    Returns:
        BM25Retriever: A keyword-based retriever object
    """
    # Create BM25 retriever with word tokenization preprocessing
    # word_tokenize splits text into individual words for indexing
    # This preprocessing ensures consistent tokenization for both indexing and querying
    return BM25Retriever.from_documents(documents, preprocess_func=word_tokenize)

def answer_question(question, documents):
    """
    Generate an answer to a question using the retrieved documents as context.
    
    This function implements the "Generation" part of RAG by:
    1. Combining all retrieved documents into a single context
    2. Using the predefined prompt template to structure the input
    3. Invoking the language model to generate a contextual answer
    
    Args:
        question (str): The user's question
        documents (list): List of relevant document chunks retrieved by the hybrid system
        
    Returns:
        str: The generated answer from the language model
    """
    # Combine all document contents into a single context string
    # Each document is separated by double newlines for better readability
    context = "\n\n".join([doc.page_content for doc in documents])
    
    # Create a prompt using the template with the question and context
    # This structures the input to the language model properly
    prompt = ChatPromptTemplate.from_template(template)
    
    # Create a chain that combines the prompt with the language model
    # The | operator creates a pipeline: prompt -> model
    chain = prompt | model

    # Invoke the chain with the question and context to get an answer
    # This is where the actual answer generation happens
    return chain.invoke({"question": question, "context": context})

# === STREAMLIT USER INTERFACE ===

# Create a file uploader widget in the Streamlit interface
# This allows users to upload PDF files through the web interface
uploaded_file = st.file_uploader(
    "Upload PDF",                    # Widget label displayed to users
    type="pdf",                      # Only allow PDF files to be uploaded
    accept_multiple_files=False      # Only allow one file at a time for simplicity
)

# Main application logic - only executes when a PDF file is uploaded
if uploaded_file:
    # Step 1: Save the uploaded file to the server
    # This stores the file locally so it can be processed
    upload_pdf(uploaded_file)
    
    # Step 2: Load and parse the PDF document
    # Extract text content from the PDF file
    documents = load_pdf(pdfs_directory + uploaded_file.name)
    
    # Step 3: Split the document into smaller, manageable chunks
    # This prepares the content for efficient retrieval
    chunked_documents = split_text(documents)

    # Step 4: Build two different types of retrievers for hybrid search
    
    # Semantic retriever: finds documents based on meaning/context
    # Uses embeddings to understand conceptual similarity
    semantic_retriever = build_semantic_retriever(chunked_documents)
    
    # BM25 retriever: finds documents based on keyword matching
    # Uses traditional information retrieval for exact term matches
    bm25_retriever = build_bm25_retriever(chunked_documents)
    
    # Step 5: Create a hybrid retriever that combines both approaches
    # This leverages the strengths of both semantic and keyword-based search
    # Semantic search handles conceptual queries, BM25 handles specific terms
    hybrid_retriever = EnsembleRetriever(
        retrievers=[semantic_retriever, bm25_retriever],  # List of retrievers to combine
        weights=[0.5, 0.5]                                # Equal weight to both methods
    )

    # Create a chat input widget for user questions
    # This provides an interface for users to ask questions about the PDF
    question = st.chat_input()

    # Process the question when user submits it
    if question:
        # Display the user's question in the chat interface
        # This creates a conversational UI experience
        st.chat_message("user").write(question)
        
        # Step 6: Retrieve relevant documents using the hybrid approach
        # This finds the most relevant chunks from the PDF based on the question
        related_documents = hybrid_retriever.invoke(question)
        
        # Step 7: Generate an answer using the retrieved documents as context
        # This combines the retrieved information to create a comprehensive answer
        answer = answer_question(question, related_documents)
        
        # Display the AI's answer in the chat interface
        # This completes the conversational loop
        st.chat_message("assistant").write(answer)

