import streamlit as st
import sys
import hashlib
from pathlib import Path

# Add the project root to the system path so we can import the pipeline
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))

from app import LegalRAGPipeline
from config.settings import UPLOADS_DIR
from src.ingestion.build_knowledge_base import index_uploaded_pdf
from src.ui.document_links import citation_pdf_url
from src.safety.incident_response import get_incident_guide


def apply_indian_legal_theme() -> None:
    """Apply presentation-only styling for the Indian legal knowledge interface."""
    st.markdown(
        """
        <style>
        :root {
            --saffron: #ff9933;
            --india-green: #138808;
            --navy: #000080;
            --ink: #08111f;
            --surface: #102238;
            --line: rgba(248, 244, 236, 0.16);
        }

        [data-testid="stAppViewContainer"] {
            background:
                radial-gradient(circle at 88% 4%, rgba(255, 153, 51, 0.12), transparent 25rem),
                radial-gradient(circle at 8% 20%, rgba(19, 136, 8, 0.10), transparent 23rem),
                linear-gradient(180deg, #0b1728 0%, var(--ink) 58%, #060c16 100%);
        }

        [data-testid="stMain"] {
            background: linear-gradient(90deg, rgba(19, 136, 8, 0.025), transparent 32%, transparent 68%, rgba(255, 153, 51, 0.035));
        }

        .block-container {
            max-width: 980px;
            padding-top: 3rem;
            padding-bottom: 2.5rem;
        }

        .legal-hero {
            position: relative;
            overflow: hidden;
            padding: 1.75rem 1.85rem 1.55rem;
            border: 1px solid var(--line);
            border-radius: 18px;
            background:
                linear-gradient(135deg, rgba(21, 43, 70, 0.98), rgba(8, 20, 37, 0.96)),
                var(--surface);
            box-shadow: 0 22px 56px rgba(0, 0, 0, 0.32), inset 0 1px 0 rgba(255, 255, 255, 0.05);
        }

        .legal-hero::after {
            content: "⚖";
            position: absolute;
            right: 1.5rem;
            bottom: -1.25rem;
            color: rgba(255, 153, 51, 0.11);
            font-size: 9rem;
            line-height: 1;
        }

        .tiranga {
            display: flex;
            align-items: center;
            height: 7px;
            width: min(220px, 48vw);
            margin-bottom: 1.2rem;
            overflow: hidden;
            border-radius: 999px;
            box-shadow: 0 0 0 1px rgba(255, 255, 255, 0.12);
            clip-path: inset(0 100% 0 0 round 999px);
            animation: tiranga-fill 1.15s cubic-bezier(0.16, 1, 0.3, 1) 0.12s forwards;
        }

        .tiranga span { display: block; height: 100%; flex: 1; }
        .tiranga .saffron { background: var(--saffron); }
        .tiranga .white { background: #fffdf6; }
        .tiranga .green { background: var(--india-green); }

        @keyframes tiranga-fill {
            from { clip-path: inset(0 100% 0 0 round 999px); }
            to { clip-path: inset(0 0 0 0 round 999px); }
        }

        .legal-kicker {
            color: var(--saffron);
            font-size: 0.78rem;
            font-weight: 700;
            letter-spacing: 0.14em;
            text-transform: uppercase;
        }

        .legal-hero h1 {
            margin: 0.3rem 0 0.45rem;
            color: #fffdf8;
            font-family: Georgia, "Times New Roman", serif;
            font-size: clamp(2rem, 5vw, 3.25rem);
            line-height: 1.08;
        }

        .legal-hero p {
            position: relative;
            z-index: 1;
            max-width: 690px;
            margin: 0;
            color: rgba(248, 244, 236, 0.82);
            font-size: 1.03rem;
            line-height: 1.6;
        }

        .legal-motto {
            position: relative;
            z-index: 1;
            display: inline-flex;
            gap: 0.5rem;
            align-items: center;
            margin-top: 1rem;
            padding: 0.42rem 0.72rem;
            border: 1px solid rgba(255, 153, 51, 0.32);
            border-radius: 999px;
            color: #fff3df;
            font-size: 0.87rem;
        }

        [data-testid="stExpander"] {
            border: 1px solid var(--line);
            border-radius: 12px;
            background: linear-gradient(135deg, rgba(23, 45, 71, 0.74), rgba(12, 27, 47, 0.72));
            box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.035);
            transition: transform 180ms ease, border-color 180ms ease, box-shadow 180ms ease, background 180ms ease;
        }

        [data-testid="stExpander"]:hover {
            transform: translateY(-3px);
            border-color: rgba(255, 153, 51, 0.48);
            background: linear-gradient(135deg, rgba(29, 56, 86, 0.86), rgba(14, 33, 56, 0.84));
            box-shadow: 0 12px 28px rgba(0, 0, 0, 0.2), inset 0 1px 0 rgba(255, 255, 255, 0.06);
        }

        [data-testid="stExpander"] summary {
            color: #fff7e9;
            font-weight: 600;
        }

        [data-testid="stExpander"] summary svg {
            transition: transform 220ms cubic-bezier(0.16, 1, 0.3, 1);
        }

        [data-testid="stExpander"] details[open] summary svg,
        [data-testid="stExpander"][open] summary svg {
            transform: rotate(90deg);
        }

        [data-testid="stChatInput"] {
            border: 1px solid rgba(255, 153, 51, 0.55);
            border-radius: 14px;
            background: linear-gradient(135deg, rgba(20, 43, 70, 0.96), rgba(12, 27, 47, 0.98));
            box-shadow: 0 12px 30px rgba(0, 0, 0, 0.22), inset 0 1px 0 rgba(255, 255, 255, 0.045);
        }

        [data-testid="stChatMessage"] {
            border-radius: 14px;
            border: 1px solid rgba(248, 244, 236, 0.07);
            background: linear-gradient(135deg, rgba(17, 37, 61, 0.62), rgba(8, 20, 36, 0.52));
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
            padding: 0.35rem 0.55rem;
        }

        [data-testid="stVerticalBlockBorderWrapper"] {
            background: linear-gradient(135deg, rgba(19, 43, 68, 0.78), rgba(10, 25, 43, 0.76));
            border-color: rgba(255, 153, 51, 0.24);
            box-shadow: 0 12px 30px rgba(0, 0, 0, 0.18), inset 0 1px 0 rgba(255, 255, 255, 0.04);
        }

        [data-testid="stLinkButton"] a {
            border-color: rgba(255, 153, 51, 0.48);
            background: rgba(255, 153, 51, 0.09);
        }

        [data-testid="stCaptionContainer"] {
            color: rgba(248, 244, 236, 0.64);
        }

        .legal-disclaimer {
            margin: 0.8rem 0 1.4rem;
            padding-left: 0.7rem;
            border-left: 3px solid var(--india-green);
            color: rgba(248, 244, 236, 0.68);
            font-size: 0.87rem;
        }

        @media (prefers-reduced-motion: reduce) {
            .tiranga,
            [data-testid="stExpander"],
            [data-testid="stExpander"] summary svg {
                animation: none;
                transition: none;
            }

            .tiranga { clip-path: none; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_citations(citations: list[dict]) -> None:
    """Render source citations as links to their local PDF evidence."""
    seen = set()
    for citation in citations:
        source = citation.get("source", "Unknown PDF")
        key = (
            source,
            citation.get("act", "Unknown"),
            citation.get("section", "Unknown"),
            citation.get("pages", "Unknown"),
        )
        if key in seen:
            continue
        seen.add(key)

        label = (
            f"{source} — Act: {citation.get('act')} | "
            f"Sec: {citation.get('section')} | Page: {citation.get('pages')}"
        )
        pdf_url = citation_pdf_url(citation)
        if pdf_url:
            st.link_button(f"📄 {label}", pdf_url, use_container_width=True)
        else:
            st.caption(f"📄 {label} (local PDF not available)")


def render_incident_guide(guide) -> None:
    """Show deterministic safety steps separately from the legal RAG answer."""
    if guide is None:
        return

    with st.container(border=True):
        st.subheader(f"🛟 {guide.title}")
        if guide.urgency_notice:
            st.error(guide.urgency_notice)
        st.caption(
            "These are practical support steps, not a substitute for emergency responders, "
            "medical care, or legal advice."
        )
        for number, step in enumerate(guide.steps, start=1):
            st.markdown(f"**{number}.** {step}")

        resource_columns = st.columns(min(2, len(guide.resources)))
        for index, (label, url) in enumerate(guide.resources):
            with resource_columns[index % len(resource_columns)]:
                st.link_button(label, url, use_container_width=True)

# -------------------------------------------------------------------
# PAGE CONFIGURATION
# -------------------------------------------------------------------
st.set_page_config(
    page_title="Nyaya | Indian Legal Knowledge",
    page_icon="⚖️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

apply_indian_legal_theme()
st.markdown(
    """
    <section class="legal-hero">
        <div class="tiranga" aria-label="Indian tricolour motif">
            <span class="saffron"></span><span class="white"></span><span class="green"></span>
        </div>
        <div class="legal-kicker">Indian legal knowledge system</div>
        <h1>Nyaya — Legal Intelligence, Grounded in Law</h1>
        <p>Explore Indian law across all domains — criminal, civil, family, consumer, digital, and more — with statute-based answers grounded in the actual text of the Acts.</p>
        <div class="legal-motto">⚖️ <span>न्याय • संविधान • विश्वास</span></div>
    </section>
    """,
    unsafe_allow_html=True,
)
st.markdown(
    "<div class='legal-disclaimer'>For legal information only. Every answer should be verified against the cited statute; consult a qualified legal professional for advice.</div>",
    unsafe_allow_html=True,
)

with st.expander("📜 Add a legal document to the knowledge library", expanded=False):
    st.caption("Upload a text-based PDF. It will be added to this assistant's searchable evidence base.")
    with st.form("document_upload_form", clear_on_submit=True):
        uploaded_pdf = st.file_uploader("PDF document", type=["pdf"])
        document_label = st.text_input(
            "Document / Act label",
            placeholder="Example: State Rules, 2025",
            help="This label appears in the retrieved-source citation.",
        )
        index_document = st.form_submit_button("Index document", type="primary")

    if index_document:
        if uploaded_pdf is None:
            st.error("Choose a PDF before indexing.")
        elif uploaded_pdf.size > 25 * 1024 * 1024:
            st.error("The PDF must be 25 MB or smaller.")
        else:
            safe_name = Path(uploaded_pdf.name).name
            content = uploaded_pdf.getvalue()
            content_hash = hashlib.sha256(content).hexdigest()[:16]
            UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
            saved_path = UPLOADS_DIR / f"{content_hash}_{safe_name}"
            try:
                if not saved_path.exists():
                    saved_path.write_bytes(content)
                with st.spinner("Extracting, embedding, and indexing the document..."):
                    stored_chunks = index_uploaded_pdf(
                        saved_path,
                        source_name=safe_name,
                        act_name=document_label.strip() or "Uploaded document",
                    )
                if not stored_chunks:
                    st.error("No readable text was found in that PDF. Scanned PDFs need OCR before upload.")
                else:
                    st.cache_resource.clear()
                    st.session_state.upload_notice = (
                        f"Indexed {stored_chunks} chunks from {safe_name}."
                    )
                    st.rerun()
            except Exception:
                st.error("The document could not be indexed. Confirm it is a valid text-based PDF and try again.")

if upload_notice := st.session_state.pop("upload_notice", None):
    st.success(upload_notice)
st.divider()

# -------------------------------------------------------------------
# INITIALIZE PIPELINE & SESSION STATE
# -------------------------------------------------------------------
@st.cache_resource
def load_pipeline():
    """Caches the backend pipeline so it doesn't reload on every UI interaction."""
    return LegalRAGPipeline()

pipeline = load_pipeline()

# Initialize chat history in Streamlit session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# -------------------------------------------------------------------
# CHAT INTERFACE
# -------------------------------------------------------------------
# Display historical messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
        # If the message is from the assistant, display the extra metadata
        if message["role"] == "assistant" and "metadata" in message:
            meta = message["metadata"]
            render_incident_guide(meta.get("incident_guide"))
            
            # Confidence Badge Layout
            col1, col2 = st.columns([1, 3])
            with col1:
                tier = meta.get("confidence_tier", "Unknown")
                score = meta.get("confidence_score", 0.0)
                
                if "High" in tier:
                    st.success(f"**{tier}** ({score}%)")
                elif "Moderate" in tier:
                    st.warning(f"**{tier}** ({score}%)")
                else:
                    st.error(f"**{tier}** ({score}%)")
            
            # Citation Drawer
            citations = meta.get("citations", [])
            if citations:
                with st.expander("📚 View evidence & source citations"):
                    render_citations(citations)

# -------------------------------------------------------------------
# USER INPUT HANDLING
# -------------------------------------------------------------------
if prompt := st.chat_input("Ask about any Indian law (e.g. 'What are the grounds for divorce?', 'What is the punishment for murder?'):"):
    
    # 1. Add user message to UI
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 2. Generate response with a loading spinner
    with st.chat_message("assistant"):
        incident_guide = get_incident_guide(prompt)
        render_incident_guide(incident_guide)
        with st.spinner("Searching Indian Law & Verifying Evidence..."):
            try:
                result = pipeline.query(prompt)
            except Exception:
                result = {
                    "answer": "I cannot process that question right now. Please try again later.",
                    "confidence_tier": "Service Unavailable",
                    "confidence_score": 0.0,
                    "citations": [],
                    "incident_guide": incident_guide,
                }
            
            answer_text = result["answer"]
            st.markdown(answer_text)
            
            # Display Confidence Badge for the current response
            col1, col2 = st.columns([1, 3])
            with col1:
                tier = result["confidence_tier"]
                score = result["confidence_score"]
                
                if "High" in tier:
                    st.success(f"**{tier}** ({score}%)")
                elif "Moderate" in tier:
                    st.warning(f"**{tier}** ({score}%)")
                else:
                    st.error(f"**{tier}** ({score}%)")
            
            # Display Citations for the current response
            citations = result.get("citations", [])
            if citations:
                with st.expander("📚 View evidence & source citations"):
                    render_citations(citations)

    # 3. Save assistant response to session state
    st.session_state.messages.append({
        "role": "assistant", 
        "content": answer_text,
        "metadata": {
            "confidence_tier": result["confidence_tier"],
            "confidence_score": result["confidence_score"],
            "citations": result["citations"],
            "incident_guide": result.get("incident_guide", incident_guide),
        }
    })
