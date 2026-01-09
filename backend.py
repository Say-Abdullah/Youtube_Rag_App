"""
Backend Logic - Simplified RAG System for YouTube Videos (Fixed)
"""
import os
import re
from typing import Optional, Tuple, Dict
from dotenv import load_dotenv

# LangChain imports
from langchain_community.document_loaders import YoutubeLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

# Load environment variables
load_dotenv()

# Set HuggingFace token if available
if os.getenv("HF_TOKEN"):
    os.environ["HF_TOKEN"] = os.getenv("HF_TOKEN")


class YouTubeRAGSystem:
    """Simplified RAG system for YouTube video transcripts"""
    
    def __init__(self):
        """Initialize the RAG system"""
        # Default configuration
        self.chunk_size = 1000
        self.chunk_overlap = 200
        self.search_k = 4
        self.temperature = 0.2
        
        # Model settings
        self.embedding_model = "sentence-transformers/all-MiniLM-L6-v2"
        self.llm_model = "llama-3.3-70b-versatile"
        
        # System components
        self.embeddings = None
        self.vector_store = None
        self.rag_chain = None
        self.transcript = None
        self.video_info = None
        
        # Initialize embeddings
        self._initialize_embeddings()
    
    def _initialize_embeddings(self):
        """Initialize the embedding model"""
        try:
            self.embeddings = HuggingFaceEmbeddings(
                model_name=self.embedding_model,
                model_kwargs={'device': 'cpu'}
            )
        except Exception as e:
            raise Exception(f"Failed to initialize embeddings: {str(e)}")
    
    def _extract_video_id(self, url: str) -> Optional[str]:
        """Extract YouTube video ID from URL"""
        patterns = [
            r'(?:youtube\.com\/watch\?v=)([^&\n?#]+)',
            r'(?:youtu\.be\/)([^&\n?#]+)',
            r'(?:youtube\.com\/embed\/)([^&\n?#]+)',
            r'(?:youtube\.com\/v\/)([^&\n?#]+)',
            r'(?:youtube\.com\/shorts\/)([^&\n?#]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    
    def _validate_url(self, url: str) -> Tuple[bool, str]:
        """Validate YouTube URL"""
        if not url or not url.strip():
            return False, "Please enter a valid YouTube URL"
        
        video_id = self._extract_video_id(url)
        if not video_id:
            return False, "Invalid YouTube URL format"
        
        return True, "Valid URL"
    
    def load_video_transcript(self, url: str) -> Tuple[bool, str, Optional[Dict]]:
        """
        Load transcript from YouTube video
        Returns: (success, message, video_info)
        """
        try:
            # Validate URL
            print("enter in transcript function")
            is_valid, message = self._validate_url(url)
            if not is_valid:
                return False, message, None
            
            print("now the url is fine")
            
            # Extract video ID for better error messages
            video_id = self._extract_video_id(url)
            print("now the url is fine")
            # Try loading transcript with multiple language options
            try:
                print("enter in fist attempt")
                # First attempt: Default languages
                loader = YoutubeLoader.from_youtube_url(
                    url, 
                    add_video_info=False,
                )
                docs = loader.load()
            except Exception as e:
                error_str = str(e).lower()
                print("if error occured",error_str)
                
                # If language issue, try without language restriction
                if "transcript" in error_str or "language" in error_str or "subtitle" in error_str:
                    try:
                        print("try second time")
                        loader = YoutubeLoader.from_youtube_url(
                            url, 
                            add_video_info=True
                        )
                        docs = loader.load()
                    except Exception as e2:
                        print("Error exist", e2)
                        # If still failing, try one more time with different approach
                        try:
                            loader = YoutubeLoader(
                                video_id=video_id,
                                add_video_info=True
                            )
                            docs = loader.load()
                        except Exception as e3:
                            print("error ocured in third try",e3)
                            return False, f"Could not load transcript. The video may not have captions enabled or available. Error: {str(e3)}", None
                else:
                    print("error cause loadind the video")
                    return False, f"Error loading video: {str(e)}", None
            
            if not docs or len(docs) == 0:
                return False, "No transcript found for this video. Please ensure the video has captions/subtitles enabled.", None
            
            # Store transcript
            self.transcript = docs[0].page_content
            
            if not self.transcript or not self.transcript.strip():
                return False, "Transcript is empty. The video may not have valid captions.", None
            
            # Extract video metadata
            metadata = docs[0].metadata
            self.video_info = {
                "title": metadata.get("title", "Unknown Title"),
                "author": metadata.get("author", "Unknown Author"),
                "length": metadata.get("length", 0),
                "view_count": metadata.get("view_count", 0),
            }
            
            return True, "Transcript loaded successfully", self.video_info
            
        except Exception as e:
            error_msg = str(e)
            
            # Provide helpful error messages
            if "HTTP Error 400" in error_msg:
                return False, "Invalid request to YouTube. Please check the URL and try again.", None
            elif "HTTP Error 403" in error_msg:
                return False, "Access forbidden. The video may be private or restricted.", None
            elif "HTTP Error 404" in error_msg:
                return False, "Video not found. Please check the URL.", None
            elif "TranscriptsDisabled" in error_msg or "disabled" in error_msg.lower():
                return False, "Transcripts are disabled for this video. Please try a different video.", None
            elif "NoTranscriptFound" in error_msg:
                return False, "No transcript available for this video. The video may not have captions.", None
            else:
                return False, f"Error loading transcript: {error_msg}", None
    
    def create_vector_database(self) -> Tuple[bool, str, Dict]:
        """
        Create vector database from transcript
        Returns: (success, message, stats)
        """
        try:
            if not self.transcript:
                return False, "No transcript loaded", {}
            
            # Split transcript into chunks
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap,
                length_function=len,
                separators=["\n\n", "\n", ". ", " ", ""]
            )
            
            chunks = text_splitter.create_documents([self.transcript])
            
            if not chunks:
                return False, "Failed to create chunks from transcript", {}
            
            # Create vector store
            self.vector_store = FAISS.from_documents(
                documents=chunks,
                embedding=self.embeddings
            )
            
            # Calculate statistics
            total_chars = sum(len(chunk.page_content) for chunk in chunks)
            stats = {
                "total_chunks": len(chunks),
                "avg_chunk_size": total_chars // len(chunks) if len(chunks) > 0 else 0,
                "total_characters": total_chars,
                "transcript_length": len(self.transcript)
            }
            
            return True, "Vector database created successfully", stats
            
        except Exception as e:
            return False, f"Error creating vector database: {str(e)}", {}
    
    def setup_rag_chain(self) -> Tuple[bool, str]:
        """
        Setup the RAG chain for question answering
        Returns: (success, message)
        """
        try:
            if not self.vector_store:
                return False, "Vector store not initialized"
            
            # Create retriever
            retriever = self.vector_store.as_retriever(
                search_type="similarity",
                search_kwargs={"k": self.search_k}
            )
            
            # Initialize LLM
            llm = ChatGroq(
                model=self.llm_model,
                temperature=self.temperature,
                max_tokens=1024
            )
            
            # Create prompt template
            template = """You are an AI assistant that answers questions based on YouTube video transcripts.

Context from the video transcript:
{context}

Question: {question}

Instructions:
- Answer ONLY based on the provided context
- Be concise and accurate
- If you don't have enough information, say "I don't have enough information in the transcript to answer this"
- Provide specific details when available
- Use natural language and be helpful

Answer:"""
            
            prompt = ChatPromptTemplate.from_template(template)
            
            # Format documents helper
            def format_docs(docs):
                return "\n\n".join(doc.page_content for doc in docs)
            
            # Build the RAG chain
            self.rag_chain = (
                {
                    "context": retriever | format_docs,
                    "question": RunnablePassthrough()
                }
                | prompt
                | llm
                | StrOutputParser()
            )
            
            return True, "RAG chain setup successfully"
            
        except Exception as e:
            return False, f"Error setting up RAG chain: {str(e)}"
    
    def process_video(self, url: str) -> Tuple[bool, str, Dict]:
        """
        Complete pipeline to process a video
        Returns: (success, message, info_dict)
        """
        # Step 1: Load transcript
        print("click the process button")
        success, message, video_info = self.load_video_transcript(url)
        if not success:
            return False, message, {}
        
        # Step 2: Create vector database
        success, message, stats = self.create_vector_database()
        if not success:
            return False, message, {}
        
        # Step 3: Setup RAG chain
        success, message = self.setup_rag_chain()
        if not success:
            return False, message, {}
        
        # Combine all information
        result = {
            "video_info": video_info,
            "stats": stats
        }
        
        return True, "Video processed successfully", result
    
    def ask_question(self, question: str) -> str:
        """
        Ask a question about the video
        Returns: Answer string
        """
        try:
            if not self.rag_chain:
                return "❌ Error: Please process a video first before asking questions."
            
            if not question or not question.strip():
                return "❌ Please enter a valid question."
            
            # Invoke the RAG chain
            answer = self.rag_chain.invoke(question)
            return answer
            
        except Exception as e:
            return f"❌ Error generating answer: {str(e)}"
    
    def update_settings(self, **kwargs):
        """Update system settings"""
        if 'chunk_size' in kwargs:
            self.chunk_size = kwargs['chunk_size']
        if 'chunk_overlap' in kwargs:
            self.chunk_overlap = kwargs['chunk_overlap']
        if 'search_k' in kwargs:
            self.search_k = kwargs['search_k']
        if 'temperature' in kwargs:
            self.temperature = kwargs['temperature']
    
    def is_ready(self) -> bool:
        """Check if system is ready to answer questions"""
        return self.rag_chain is not None
    
    def reset(self):
        """Reset the system to initial state"""
        self.vector_store = None
        self.rag_chain = None
        self.transcript = None
        self.video_info = None


# Utility functions
def format_duration(seconds: int) -> str:
    """Convert seconds to readable duration format"""
    if seconds <= 0:
        return "0s"
    
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    
    parts = []
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    if secs > 0 or not parts:
        parts.append(f"{secs}s")
    
    return " ".join(parts)


def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text to maximum length with ellipsis"""
    if not text:
        return ""
    if len(text) <= max_length:
        return text
    return text[:max_length].strip() + "..."


def format_number(num: int) -> str:
    """Format large numbers with commas"""
    return f"{num:,}"

if __name__ == "__main__":
    rag = YouTubeRAGSystem()

    url = input("Enter YouTube URL: ").strip()
    success, message, info = rag.process_video(url)
    print(message)

    if not success:
        exit(1)

    print("\nVideo Info:", info.get("video_info", {}))
    print("Stats:", info.get("stats", {}))

    while True:
        question = input("\nAsk a question (or type 'exit'): ").strip()
        if question.lower() == "exit":
            break
        print("\nAnswer:", rag.ask_question(question))
