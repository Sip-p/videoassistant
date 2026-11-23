
import streamlit as st

from main import run_pipeline


# ---------------- PAGE CONFIG ----------------

st.set_page_config(
    page_title="VideoMind AI",
    page_icon="🎬",
    layout="wide"
)


# ---------------- CUSTOM CSS ----------------

st.markdown("""
<style>
    .main {
        background-color: #0e1117;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    .hero {
        padding: 25px;
        border-radius: 15px;
        background: linear-gradient(120deg, #172554, #312e81);
        margin-bottom: 25px;
    }

    .hero h1 {
        color: white;
        font-size: 38px;
        margin-bottom: 5px;
    }

    .hero p {
        color: #cbd5e1;
        font-size: 16px;
    }

    div[data-testid="stMetric"] {
        background-color: #1e293b;
        padding: 15px;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)


# ---------------- SESSION STATE ----------------

if "result" not in st.session_state:
    st.session_state.result = None

if "messages" not in st.session_state:
    st.session_state.messages = []


# ---------------- HEADER ----------------

st.markdown("""
<div class="hero">
    <h1>🎬 VideoMind AI</h1>
    <p>
        Transform long videos into meaningful summaries,
        decisions and actionable insights.
    </p>
</div>
""", unsafe_allow_html=True)


# ---------------- SIDEBAR ----------------

with st.sidebar:
    st.title("⚙️ Settings")

    language = st.selectbox(
        "Transcription language",
        ["english", "hinglish"]
    )

    st.divider()

    st.markdown("### 🧠 Powered by")
    st.write("🎙️ OpenAI Whisper")
    st.write("🤖 Groq LLM")
    st.write("🔎 Hugging Face Embeddings")
    st.write("🗄️ ChromaDB")
    st.write("🔗 LangChain RAG")

    st.divider()

    if st.button("🗑️ Clear current session"):
        st.session_state.result = None
        st.session_state.messages = []
        st.rerun()


# ---------------- VIDEO INPUT ----------------

st.subheader("📥 Process your video")

source = st.text_input(
    "YouTube URL or local video/audio file path",
    placeholder="https://www.youtube.com/watch?v=..."
)

process_button = st.button(
    "🚀 Process Video",
    type="primary",
    use_container_width=True
)


if process_button:

    if not source.strip():
        st.warning("Please enter a YouTube URL or file path.")

    else:
        try:
            with st.spinner(
                "Processing video... This may take some time."
            ):
                result = run_pipeline(
                    source.strip(),
                    language
                )

                st.session_state.result = result
                st.session_state.messages = []

            st.success("Video processed successfully!")

        except Exception as e:
            st.error(f"Something went wrong: {str(e)}")


# ---------------- DISPLAY RESULTS ----------------

result = st.session_state.result

if result:

    st.divider()

    st.subheader("📊 Meeting Overview")

    st.title(f"🎯 {result['title']}")

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📝 Summary",
        "✅ Action Items",
        "💡 Key Decisions",
        "❓ Open Questions",
        "📄 Transcript"
    ])

    with tab1:
        st.markdown("### Meeting Summary")
        st.write(result["summary"])

    with tab2:
        st.markdown("### Action Items")
        st.write(result["action_items"])

    with tab3:
        st.markdown("### Key Decisions")
        st.write(result["key_decisions"])

    with tab4:
        st.markdown("### Unresolved Questions")
        st.write(result["open_questions"])

    with tab5:
        st.markdown("### Full Transcript")
        st.text_area(
            "Transcript",
            value=result["transcript"],
            height=400
        )

    # ---------------- CHAT WITH VIDEO ----------------

    st.divider()

    st.subheader("💬 Chat with your video")

    st.caption(
        "Ask questions based on the information in your video."
    )

    rag_chain = result["rag_chain"]

    # Display previous messages
    for message in st.session_state.messages:

        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    question = st.chat_input(
        "Ask something about your video..."
    )

    if question:

        # Display user message
        st.session_state.messages.append({
            "role": "user",
            "content": question
        })

        with st.chat_message("user"):
            st.markdown(question)

        # Generate AI response
        with st.chat_message("assistant"):

            with st.spinner("Thinking..."):

                try:
                    answer = rag_chain.invoke(question)

                    st.markdown(answer)

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer
                    })

                except Exception as e:
                    st.error(f"Error generating answer: {str(e)}")

else:

    st.info(
        "👆 Enter a video URL or local file path above to get started."
    )
