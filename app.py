"""
Streamlit Frontend - YouTube RAG Assistant
Beautiful, Modern Design with Scrollable Sidebar
"""
import streamlit as st
from backend import YouTubeRAGSystem, format_duration, truncate_text, format_number

# Page configuration
st.set_page_config(
    page_title="YouTube RAG Assistant",
    page_icon="🎥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS - Beautiful Design with Good Contrast
st.markdown("""
    <style>
    /* Global Styles */
    .main {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 50%, #7e22ce 100%);
        background-attachment: fixed;
        padding: 0 !important;
    }
    
    .block-container {
        padding: 2rem 3rem !important;
        max-width: 1400px;
        background: rgba(255, 255, 255, 0.98);
        border-radius: 20px;
        box-shadow: 0 25px 70px rgba(0, 0, 0, 0.4);
        margin: 2rem auto !important;
        backdrop-filter: blur(15px);
    }
    
    /* Sidebar Styles with Scrolling */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e3c72 0%, #2a5298 50%, #7e22ce 100%) !important;
        border-right: 3px solid rgba(255, 255, 255, 0.2);
    }
    
    section[data-testid="stSidebar"] > div {
        background: transparent;
        padding: 1.5rem 1rem;
        overflow-y: auto !important;
        max-height: 100vh;
    }
    
    /* Sidebar scrollbar */
    section[data-testid="stSidebar"] > div::-webkit-scrollbar {
        width: 8px;
    }
    
    section[data-testid="stSidebar"] > div::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
    }
    
    section[data-testid="stSidebar"] > div::-webkit-scrollbar-thumb {
        background: rgba(255, 255, 255, 0.4);
        border-radius: 10px;
    }
    
    section[data-testid="stSidebar"] > div::-webkit-scrollbar-thumb:hover {
        background: rgba(255, 255, 255, 0.6);
    }
    
    /* Sidebar text colors for contrast */
    section[data-testid="stSidebar"] .element-container {
        color: white !important;
    }
    
    section[data-testid="stSidebar"] label {
        color: rgba(255, 255, 255, 0.95) !important;
        font-weight: 600 !important;
    }
    
    section[data-testid="stSidebar"] p {
        color: rgba(255, 255, 255, 0.9) !important;
    }
    
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        color: white !important;
    }
    
    /* Info box in sidebar */
    section[data-testid="stSidebar"] .stAlert {
        background: rgba(255, 255, 255, 0.15) !important;
        border-left: 4px solid #fbbf24 !important;
        color: white !important;
        backdrop-filter: blur(10px);
    }
    
    /* Headers */
    h1 {
        background: linear-gradient(135deg, #1e3c72 0%, #7e22ce 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 3.8rem !important;
        font-weight: 900 !important;
        text-align: center;
        margin-bottom: 0.3rem !important;
        letter-spacing: -1px;
    }
    
    h2 {
        color: #1e3c72;
        font-weight: 800;
        margin-top: 2.5rem;
        margin-bottom: 1.5rem;
        font-size: 2rem !important;
    }
    
    h3 {
        color: #7e22ce;
        font-weight: 600;
        text-align: center;
        margin-bottom: 2rem;
        font-size: 1.3rem !important;
    }
    
    /* Video Info Box */
    .video-info-box {
        background: linear-gradient(135deg, #1e3c72 0%, #7e22ce 100%);
        padding: 2rem;
        border-radius: 1.5rem;
        color: white;
        margin: 1.5rem 0;
        box-shadow: 0 15px 40px rgba(30, 60, 114, 0.5);
        transition: all 0.3s ease;
        border: 2px solid rgba(255, 255, 255, 0.1);
    }
    
    .video-info-box:hover {
        transform: translateY(-8px);
        box-shadow: 0 20px 50px rgba(126, 34, 206, 0.6);
    }
    
    .video-info-box h4 {
        color: white !important;
        font-size: 1.3rem !important;
        margin-bottom: 1rem !important;
        font-weight: 700 !important;
    }
    
    .video-info-box p {
        color: rgba(255, 255, 255, 0.95) !important;
        font-size: 1.05rem;
        margin: 0.7rem 0;
        font-weight: 500;
    }
    
    /* Metric Cards */
    .metric-card {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        padding: 2rem 1.5rem;
        border-radius: 1.2rem;
        border-left: 6px solid #1e3c72;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.12);
        transition: all 0.3s ease;
        text-align: center;
        border: 1px solid rgba(30, 60, 114, 0.1);
    }
    
    .metric-card:hover {
        transform: translateY(-8px) scale(1.02);
        box-shadow: 0 12px 35px rgba(30, 60, 114, 0.25);
        border-left-color: #7e22ce;
    }
    
    .metric-card h4 {
        color: #1e3c72;
        margin-bottom: 0.8rem;
        font-size: 1.1rem;
        font-weight: 700;
    }
    
    .metric-card h2 {
        color: #7e22ce;
        margin: 0 !important;
        font-size: 2.8rem !important;
        font-weight: 900 !important;
    }
    
    /* Chat Messages */
    .chat-message {
        padding: 1.8rem;
        border-radius: 1.2rem;
        margin: 1.2rem 0;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
        border: 1px solid rgba(0, 0, 0, 0.05);
    }
    
    .chat-message:hover {
        transform: translateX(8px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
    }
    
    .user-message {
        background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
        border-left: 6px solid #2563eb;
    }
    
    .assistant-message {
        background: linear-gradient(135deg, #fae8ff 0%, #f3e8ff 100%);
        border-left: 6px solid #a855f7;
    }
    
    .chat-message strong {
        font-size: 1.15rem;
        display: block;
        margin-bottom: 0.8rem;
    }
    
    .chat-message p {
        font-size: 1.05rem;
        line-height: 1.7;
        margin: 0;
        color: #334155;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #1e3c72 0%, #7e22ce 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 1.2rem !important;
        padding: 1.2rem 3rem !important;
        font-weight: 800 !important;
        font-size: 1.15rem !important;
        width: 100% !important;
        box-shadow: 0 10px 30px rgba(30, 60, 114, 0.4) !important;
        transition: all 0.3s ease !important;
        cursor: pointer !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #7e22ce 0%, #1e3c72 100%) !important;
        box-shadow: 0 15px 40px rgba(126, 34, 206, 0.6) !important;
        transform: translateY(-4px) scale(1.02) !important;
    }
    
    .stButton > button:active {
        transform: translateY(-1px) scale(0.98) !important;
    }
    
    /* Input Fields */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        border-radius: 1rem !important;
        border: 2px solid #cbd5e1 !important;
        padding: 1.2rem !important;
        font-size: 1.05rem !important;
        transition: all 0.3s ease !important;
        background: white !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #1e3c72 !important;
        box-shadow: 0 0 0 4px rgba(30, 60, 114, 0.15) !important;
    }
    
    /* Labels */
    .stTextInput > label,
    .stTextArea > label {
        color: #1e3c72 !important;
        font-weight: 700 !important;
        font-size: 1.1rem !important;
        margin-bottom: 0.5rem !important;
    }
    
    /* Progress Bar */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #1e3c72 0%, #7e22ce 100%) !important;
    }
    
    /* Alert Messages */
    .stAlert {
        border-radius: 1rem !important;
        padding: 1.2rem 1.8rem !important;
        border-left: 6px solid !important;
        font-size: 1.05rem !important;
        font-weight: 600 !important;
    }
    
    /* Success Alert */
    div[data-baseweb="notification"][kind="success"] {
        background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%) !important;
        border-left-color: #10b981 !important;
    }
    
    /* Error Alert */
    div[data-baseweb="notification"][kind="error"] {
        background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%) !important;
        border-left-color: #ef4444 !important;
    }
    
    /* Form */
    .stForm {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        padding: 2.5rem;
        border-radius: 1.5rem;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        border: 2px solid rgba(30, 60, 114, 0.1);
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: rgba(255, 255, 255, 0.2) !important;
        border-radius: 1rem !important;
        font-weight: 700 !important;
        color: white !important;
        padding: 1rem !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
    }
    
    .streamlit-expanderHeader:hover {
        background: rgba(255, 255, 255, 0.3) !important;
    }
    
    /* Slider */
    .stSlider > div > div > div > div {
        background: linear-gradient(90deg, #1e3c72 0%, #7e22ce 100%) !important;
    }
    
    /* Footer */
    .footer-style {
        text-align: center;
        color: #64748b;
        padding: 3rem 0 2rem 0;
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        border-radius: 1.5rem;
        margin-top: 4rem;
        box-shadow: 0 -8px 20px rgba(0, 0, 0, 0.06);
    }
    
    .footer-style p {
        margin: 0.5rem 0;
    }
    
    /* Animations */
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .block-container {
        animation: slideIn 0.6s ease-out;
    }
    
    /* Spinner */
    .stSpinner > div {
        border-top-color: #1e3c72 !important;
    }
    
    /* Remove extra padding */
    .main .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
    }
    
    /* Divider */
    hr {
        margin: 2.5rem 0 !important;
        border: none !important;
        height: 2px !important;
        background: linear-gradient(90deg, transparent, #cbd5e1, transparent) !important;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
def init_session_state():
    """Initialize all session state variables"""
    if 'rag_system' not in st.session_state:
        st.session_state.rag_system = YouTubeRAGSystem()
    if 'processed' not in st.session_state:
        st.session_state.processed = False
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'video_info' not in st.session_state:
        st.session_state.video_info = {}
    if 'stats' not in st.session_state:
        st.session_state.stats = {}

init_session_state()

# Sidebar
with st.sidebar:

    
    # About Section
    st.markdown("<h2 style='color: white; text-align: center; font-size: 1.5rem; margin-bottom: 1rem;'>📚 About</h2>", unsafe_allow_html=True)
    st.info(
        "🚀 **AI-Powered Video Analysis**\n\n"
        "This application uses advanced RAG (Retrieval-Augmented Generation) "
        "technology to help you understand and interact with YouTube videos."
    )
    
    # How to Use Section
    st.markdown("<h2 style='color: white; text-align: center; font-size: 1.5rem; margin: 2rem 0 1rem 0;'>📖 How to Use</h2>", unsafe_allow_html=True)
    st.markdown("""
    <div style='background: rgba(255, 255, 255, 0.15); padding: 1.5rem; border-radius: 1rem; color: white; font-size: 1.05rem; line-height: 2; backdrop-filter: blur(10px); border: 1px solid rgba(255, 255, 255, 0.2);'>
        <strong>1.</strong> 📝 Paste a YouTube URL<br>
        <strong>2.</strong> 🔄 Click Process Video<br>
        <strong>3.</strong> 💬 Ask your questions<br>
        <strong>4.</strong> 🤖 Get instant answers
    </div>
    """, unsafe_allow_html=True)
    
    # Settings Section
    st.markdown("<h2 style='color: white; text-align: center; font-size: 1.5rem; margin: 2rem 0 1rem 0;'>⚙️ Settings</h2>", unsafe_allow_html=True)
    
    with st.expander("🔧 Advanced Configuration"):
        chunk_size = st.slider("Chunk Size", 500, 2000, 1000, 100, 
                               help="Size of text chunks for processing")
        chunk_overlap = st.slider("Chunk Overlap", 50, 500, 200, 50,
                                  help="Overlap between consecutive chunks")
        search_k = st.slider("Results to Retrieve", 2, 10, 4, 1,
                            help="Number of relevant chunks to retrieve")
        temperature = st.slider("AI Temperature", 0.0, 1.0, 0.2, 0.1,
                               help="Controls randomness in responses")
        
        if st.button("✅ Apply Settings"):
            st.session_state.rag_system.update_settings(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                search_k=search_k,
                temperature=temperature
            )
            st.success("✅ Settings Applied!")
    
    # Model Information
    st.markdown("<div style='margin-top: 2rem; padding: 1.5rem; background: rgba(255, 255, 255, 0.1); border-radius: 1rem; backdrop-filter: blur(10px); border: 1px solid rgba(255, 255, 255, 0.2);'><strong> Models Information </strong>", unsafe_allow_html=True)
    st.markdown("<p style='color: white; text-align: center; margin: 0.3rem 0;'><strong>🤖 LLM Model:</strong><br>Llama 3.3 70B</p>", unsafe_allow_html=True)
    st.markdown("<p style='color: white; text-align: center; margin: 0.3rem 0;'><strong>🧠 Embeddings:</strong><br>MiniLM-L6-v2</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Clear Session Button
    st.markdown("<div style='margin-top: 2rem;'>", unsafe_allow_html=True)
    if st.button("🗑️ Clear Session", use_container_width=True):
        st.session_state.rag_system.reset()
        st.session_state.processed = False
        st.session_state.chat_history = []
        st.session_state.video_info = {}
        st.session_state.stats = {}
        st.success("✨ Session Cleared!")
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# Main Content Header
st.title("🎥 YouTube RAG Assistant")
st.markdown("### 🤖 Ask questions about any YouTube video using AI-powered analysis")

# Main Content Layout
col1, col2 = st.columns([2, 1], gap="large")

with col1:
    st.markdown("## 📹 Video Input")
    
    # YouTube URL input
    youtube_url = st.text_input(
        "Enter YouTube Video URL",
        placeholder="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        help="Paste the complete URL of any YouTube video",
        label_visibility="visible"
    )
    
    # Process button
    process_button = st.button("🔄 Process Video", use_container_width=True)
    
    # Status indicator
    if st.session_state.processed:
        st.success("✅ **Video Processed!** Ready to answer your questions.")

with col2:
    # Video Information Display
    if st.session_state.processed and st.session_state.video_info:
        st.markdown("## 📊 Video Details")
        info = st.session_state.video_info
        
        st.markdown(f"""
        <div class="video-info-box">
            <h4>📌 {truncate_text(info.get('title', 'Unknown'), 45)}</h4>
            <p><strong>👤 Creator:</strong> {info.get('author', 'Unknown')}</p>
            <p><strong>⏱️ Duration:</strong> {format_duration(info.get('length', 0))}</p>
            <p><strong>👁️ Views:</strong> {format_number(info.get('view_count', 0))}</p>
        </div>
        """, unsafe_allow_html=True)

# Process Video Handler
if process_button:
    if not youtube_url or not youtube_url.strip():
        st.error("❌ Please enter a valid YouTube URL")
    else:
        with st.spinner("🔄 Processing video... Please wait..."):
            progress_bar = st.progress(0, text="Starting...")
            
            try:
                # Update progress
                progress_bar.progress(25, text="📥 Loading transcript...")
                
                # Process the video
                success, message, info = st.session_state.rag_system.process_video(youtube_url)
                
                if not success:
                    st.error(f"❌ {message}")
                else:
                    progress_bar.progress(100, text="✅ Complete!")
                    
                    # Store information
                    st.session_state.video_info = info.get("video_info", {})
                    st.session_state.stats = info.get("stats", {})
                    st.session_state.processed = True
                    st.session_state.chat_history = []
                    
                    st.success("🎉 Video processed successfully! You can now ask questions.")
                    st.balloons()
                
            except Exception as e:
                st.error(f"❌ Unexpected error: {str(e)}")
                st.session_state.processed = False

# Statistics Display
if st.session_state.processed and st.session_state.stats:
    st.markdown("---")
    st.markdown("## 📈 Processing Statistics")
    
    stat_col1, stat_col2, stat_col3 = st.columns(3)
    stats = st.session_state.stats
    
    with stat_col1:
        st.markdown(f"""
        <div class="metric-card">
            <h4>📦 Total Chunks</h4>
            <h2>{stats.get('total_chunks', 0)}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with stat_col2:
        st.markdown(f"""
        <div class="metric-card">
            <h4>📏 Avg Size</h4>
            <h2>{stats.get('avg_chunk_size', 0)}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with stat_col3:
        st.markdown(f"""
        <div class="metric-card">
            <h4>📝 Total Chars</h4>
            <h2>{format_number(stats.get('total_characters', 0))}</h2>
        </div>
        """, unsafe_allow_html=True)

# Chat Interface
if st.session_state.processed:
    st.markdown("---")
    st.markdown("## 💬 Question & Answer")
    
    # Display chat history
    if st.session_state.chat_history:
        st.markdown("### 📜 Conversation History")
        
        for idx, message in enumerate(st.session_state.chat_history):
            if message["role"] == "user":
                st.markdown(f"""
                <div class="chat-message user-message">
                    <strong>👤 You</strong>
                    <p>{message['content']}</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="chat-message assistant-message">
                    <strong>🤖 AI Assistant</strong>
                    <p>{message['content']}</p>
                </div>
                """, unsafe_allow_html=True)
    
    # Question input form
    with st.form(key="question_form", clear_on_submit=True):
        question = st.text_area(
            "💭 Your Question",
            placeholder="What is this video about? Can you summarize the main points? What did the speaker say about...?",
            height=130,
            help="Ask anything about the video content",
            label_visibility="visible"
        )
        
        submit_col1, submit_col2 = st.columns([3, 1])
        with submit_col1:
            submit_button = st.form_submit_button("🚀 Ask Question", use_container_width=True)
    
    # Handle question submission
    if submit_button and question and question.strip():
        # Add user message to history
        st.session_state.chat_history.append({
            "role": "user",
            "content": question.strip()
        })
        
        # Generate answer
        with st.spinner("🤔 Thinking... Analyzing the video..."):
            answer = st.session_state.rag_system.ask_question(question.strip())
            
            # Add assistant message to history
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": answer
            })
        
        # Rerun to display new messages
        st.rerun()

# Footer
st.markdown("""
<div class="footer-style">
    <p style="font-size: 1.4rem; font-weight: 800; color: #1e3c72; margin-bottom: 0.5rem;">
        🎥 YouTube RAG Assistant
    </p>
    <p style="font-size: 1.05rem; color: #64748b; font-weight: 600;">
        Powered by LangChain, Groq & FAISS
    </p>
    <p style="font-size: 0.95rem; color: #94a3b8; margin-top: 1rem;">
        Built with ❤️ using Streamlit | AI-Enhanced Video Understanding
    </p>
</div>
""", unsafe_allow_html=True)