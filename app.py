import streamlit as st
import time
import io
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from pipeline import LegalNegotiatorPipeline
from utils.document_parser import extract_text_from_pdf, clean_contract_text

st.set_page_config(
    page_title="LexAI — Legal Clause Negotiator",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---- PREMIUM CSS WITH ANIMATIONS ----
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=Inter:wght@300;400;500;600&display=swap');

/* ---- GLOBAL ---- */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

#MainMenu {visibility: hidden;}
header {visibility: hidden;}
footer {visibility: hidden;}
.stApp {
    background: linear-gradient(135deg, #0a0e1a 0%, #0f1729 50%, #0a0e1a 100%);
    color: #e2e8f0;
}

/* ---- ANIMATED HEADER ---- */
.hero-header {
    text-align: center;
    padding: 40px 20px 20px;
    animation: fadeInDown 1s ease;
}

.hero-title {
    font-family: 'Playfair Display', serif;
    font-size: 3.5em;
    font-weight: 700;
    background: linear-gradient(135deg, #f6d365 0%, #fda085 50%, #f6d365 100%);
    background-size: 200% auto;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: shimmer 3s linear infinite, fadeInDown 1s ease;
}

.hero-subtitle {
    font-size: 1.1em;
    color: #94a3b8;
    letter-spacing: 3px;
    text-transform: uppercase;
    animation: fadeInUp 1.2s ease;
}

/* ---- ANIMATIONS ---- */
@keyframes shimmer {
    0% { background-position: 0% center; }
    100% { background-position: 200% center; }
}

@keyframes fadeInDown {
    from { opacity: 0; transform: translateY(-30px); }
    to { opacity: 1; transform: translateY(0); }
}

@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(30px); }
    to { opacity: 1; transform: translateY(0); }
}

@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}

@keyframes pulse {
    0%, 100% { box-shadow: 0 0 20px rgba(246, 211, 101, 0.4); }
    50% { box-shadow: 0 0 40px rgba(246, 211, 101, 0.8); }
}

@keyframes countUp {
    from { opacity: 0; transform: scale(0.5); }
    to { opacity: 1; transform: scale(1); }
}

@keyframes slideInLeft {
    from { opacity: 0; transform: translateX(-40px); }
    to { opacity: 1; transform: translateX(0); }
}

@keyframes slideInRight {
    from { opacity: 0; transform: translateX(40px); }
    to { opacity: 1; transform: translateX(0); }
}

/* ---- GLOWING BUTTON ---- */
.stButton > button {
    background: linear-gradient(135deg, #f6d365 0%, #fda085 100%) !important;
    color: #0a0e1a !important;
    font-weight: 700 !important;
    font-size: 1.1em !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 16px 32px !important;
    animation: pulse 2s infinite !important;
    transition: transform 0.2s ease !important;
    letter-spacing: 1px !important;
}

.stButton > button:hover {
    transform: scale(1.03) !important;
    animation: none !important;
    box-shadow: 0 0 60px rgba(246, 211, 101, 0.9) !important;
}

/* ---- CARDS ---- */
.premium-card {
    background: linear-gradient(135deg, #1a2035 0%, #1e2640 100%);
    border: 1px solid rgba(246, 211, 101, 0.15);
    border-radius: 16px;
    padding: 24px;
    margin: 12px 0;
    animation: fadeInUp 0.6s ease;
    transition: transform 0.3s ease, border-color 0.3s ease;
}

.premium-card:hover {
    transform: translateY(-4px);
    border-color: rgba(246, 211, 101, 0.4);
}

/* ---- RISK BADGES ---- */
.risk-badge-critical {
    background: linear-gradient(135deg, #7f1d1d, #dc2626);
    color: white;
    padding: 6px 16px;
    border-radius: 20px;
    font-weight: 700;
    font-size: 0.85em;
    letter-spacing: 1px;
    display: inline-block;
    animation: countUp 0.5s ease;
}

.risk-badge-high {
    background: linear-gradient(135deg, #78350f, #d97706);
    color: white;
    padding: 6px 16px;
    border-radius: 20px;
    font-weight: 700;
    font-size: 0.85em;
    letter-spacing: 1px;
    display: inline-block;
    animation: countUp 0.5s ease;
}

.risk-badge-medium {
    background: linear-gradient(135deg, #713f12, #ca8a04);
    color: white;
    padding: 6px 16px;
    border-radius: 20px;
    font-weight: 700;
    font-size: 0.85em;
    letter-spacing: 1px;
    display: inline-block;
}

.risk-badge-low {
    background: linear-gradient(135deg, #14532d, #16a34a);
    color: white;
    padding: 6px 16px;
    border-radius: 20px;
    font-weight: 700;
    font-size: 0.85em;
    letter-spacing: 1px;
    display: inline-block;
}

/* ---- RISK SCORE CIRCLE ---- */
.score-circle {
    width: 80px;
    height: 80px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.6em;
    font-weight: 700;
    animation: countUp 0.8s ease;
    margin: auto;
}

.score-critical { background: radial-gradient(circle, #dc2626, #7f1d1d); color: white; box-shadow: 0 0 20px rgba(220,38,38,0.5); }
.score-high { background: radial-gradient(circle, #d97706, #78350f); color: white; box-shadow: 0 0 20px rgba(217,119,6,0.5); }
.score-medium { background: radial-gradient(circle, #ca8a04, #713f12); color: white; box-shadow: 0 0 20px rgba(202,138,4,0.5); }
.score-low { background: radial-gradient(circle, #16a34a, #14532d); color: white; box-shadow: 0 0 20px rgba(22,163,74,0.5); }

/* ---- RISK BAR ---- */
.risk-bar-container {
    background: #1a2035;
    border-radius: 10px;
    height: 10px;
    width: 100%;
    margin: 8px 0;
    overflow: hidden;
}

.risk-bar-fill {
    height: 100%;
    border-radius: 10px;
    transition: width 1s ease;
    animation: slideInLeft 1s ease;
}

/* ---- CLAUSE BOXES ---- */
.clause-original {
    background: rgba(220, 38, 38, 0.08);
    border: 1px solid rgba(220, 38, 38, 0.3);
    border-radius: 12px;
    padding: 16px;
    font-family: monospace;
    font-size: 0.85em;
    line-height: 1.6;
    animation: slideInLeft 0.6s ease;
}

.clause-suggested {
    background: rgba(37, 99, 235, 0.08);
    border: 1px solid rgba(37, 99, 235, 0.3);
    border-radius: 12px;
    padding: 16px;
    font-size: 0.9em;
    line-height: 1.6;
    animation: slideInRight 0.6s ease;
}

/* ---- SIDEBAR ---- */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f1729 0%, #0a0e1a 100%);
    border-right: 1px solid rgba(246, 211, 101, 0.15);
}

/* ---- TABS ---- */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(26, 32, 53, 0.8);
    border-radius: 12px;
    padding: 4px;
    gap: 4px;
}

.stTabs [data-baseweb="tab"] {
    border-radius: 10px;
    color: #94a3b8;
    font-weight: 600;
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #f6d365, #fda085) !important;
    color: #0a0e1a !important;
}

/* ---- INPUT AREAS ---- */
.stTextArea textarea {
    background: #1a2035 !important;
    border: 1px solid rgba(246, 211, 101, 0.2) !important;
    border-radius: 12px !important;
    color: #e2e8f0 !important;
}

.stTextArea textarea:focus {
    border-color: rgba(246, 211, 101, 0.6) !important;
    box-shadow: 0 0 20px rgba(246, 211, 101, 0.1) !important;
}

/* ---- FILE UPLOADER ---- */
[data-testid="stFileUploader"] {
    background: #1a2035 !important;
    border: 2px dashed rgba(246, 211, 101, 0.3) !important;
    border-radius: 12px !important;
}

/* ---- METRICS ---- */
[data-testid="stMetric"] {
    background: linear-gradient(135deg, #1a2035, #1e2640);
    border: 1px solid rgba(246, 211, 101, 0.15);
    border-radius: 12px;
    padding: 16px;
    animation: countUp 0.8s ease;
}

[data-testid="stMetricValue"] {
    color: #f6d365 !important;
    font-size: 2em !important;
    font-weight: 700 !important;
}

/* ---- EXPANDER ---- */
[data-testid="stExpander"] {
    background: #1a2035 !important;
    border: 1px solid rgba(246, 211, 101, 0.15) !important;
    border-radius: 12px !important;
    margin: 8px 0 !important;
}

/* ---- DIVIDER ---- */
hr {
    border-color: rgba(246, 211, 101, 0.15) !important;
}

/* ---- SUMMARY BOX ---- */
.summary-box {
    background: linear-gradient(135deg, #1a2035, #1e2640);
    border: 1px solid rgba(246, 211, 101, 0.3);
    border-radius: 16px;
    padding: 28px;
    font-size: 1.05em;
    line-height: 1.8;
    color: #e2e8f0;
    animation: fadeIn 1s ease;
}

/* ---- AGENT STEPS ---- */
.agent-step {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 10px 0;
    border-bottom: 1px solid rgba(246, 211, 101, 0.08);
    animation: slideInLeft 0.5s ease;
}

.agent-dot {
    width: 10px;
    height: 10px;
    border-radius: 50%;
    background: linear-gradient(135deg, #f6d365, #fda085);
    box-shadow: 0 0 8px rgba(246, 211, 101, 0.6);
}

.download-btn > button {
    background: linear-gradient(135deg, #1a2035, #1e2640) !important;
    color: #f6d365 !important;
    border: 1px solid rgba(246, 211, 101, 0.4) !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
}
</style>
""", unsafe_allow_html=True)


# ---- HELPER FUNCTIONS ----
@st.cache_resource
def get_pipeline():
    return LegalNegotiatorPipeline()

def get_risk_info(score):
    if score >= 8:
        return "critical", "CRITICAL", "#dc2626"
    if score >= 6:
        return "high", "HIGH", "#d97706"
    if score >= 4:
        return "medium", "MEDIUM", "#ca8a04"
    return "low", "LOW", "#16a34a"

def risk_emoji(score):
    if score >= 8: return "🔴"
    if score >= 6: return "🟠"
    if score >= 4: return "🟡"
    return "🟢"

def render_risk_bar(score):
    level, label, color = get_risk_info(score)
    width = score * 10
    return f"""
    <div class="risk-bar-container">
        <div class="risk-bar-fill" style="width:{width}%; background: linear-gradient(90deg, {color}88, {color});"></div>
    </div>
    """

def generate_pdf_report(result):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                            rightMargin=inch, leftMargin=inch,
                            topMargin=inch, bottomMargin=inch)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('CustomTitle', parent=styles['Title'],
                                  fontSize=24, textColor=colors.HexColor('#1e3a5f'), spaceAfter=6)
    heading_style = ParagraphStyle('CustomHeading', parent=styles['Heading1'],
                                    fontSize=14, textColor=colors.HexColor('#1e3a5f'),
                                    spaceBefore=16, spaceAfter=6)
    subheading_style = ParagraphStyle('CustomSubHeading', parent=styles['Heading2'],
                                       fontSize=12, textColor=colors.HexColor('#2563eb'),
                                       spaceBefore=10, spaceAfter=4)
    normal_style = ParagraphStyle('CustomNormal', parent=styles['Normal'],
                                   fontSize=10, spaceAfter=6, leading=14)
    story = []
    story.append(Paragraph("⚖️ LexAI — Legal Clause Negotiator", title_style))
    story.append(Paragraph("Contract Analysis Report", styles['Heading2']))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#1e3a5f')))
    story.append(Spacer(1, 12))
    story.append(Paragraph("Executive Summary", heading_style))
    if result.plain_english_summary:
        story.append(Paragraph(result.plain_english_summary, normal_style))
    story.append(Spacer(1, 10))
    if result.risk_assessments:
        story.append(Paragraph("Risk Overview", heading_style))
        avg_score = sum(r.risk_score for r in result.risk_assessments) / len(result.risk_assessments)
        table_data = [['Clause', 'Risk Score', 'Risk Level']]
        for r in result.risk_assessments:
            _, label, _ = get_risk_info(r.risk_score)
            table_data.append([r.clause_name.replace('_', ' ').title(), f"{r.risk_score}/10", label])
        table = Table(table_data, colWidths=[3*inch, 1.5*inch, 1.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1e3a5f')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#f8fafc'), colors.white]),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
            ('FONTSIZE', (0,1), (-1,-1), 10),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ]))
        story.append(table)
        story.append(Spacer(1, 6))
        story.append(Paragraph(f"Average Risk Score: {avg_score:.1f}/10 | Highest: {max(r.risk_score for r in result.risk_assessments)}/10 | Clauses: {len(result.risk_assessments)}", normal_style))
    if result.risk_assessments:
        story.append(Paragraph("Detailed Risk Analysis", heading_style))
        for r in result.risk_assessments:
            story.append(Paragraph(f"{r.clause_name.replace('_', ' ').title()} — {r.risk_score}/10", subheading_style))
            story.append(Paragraph(r.risk_explanation, normal_style))
            for factor in r.risk_factors:
                story.append(Paragraph(f"• {factor}", normal_style))
            story.append(Spacer(1, 6))
    if result.negotiation_suggestions:
        story.append(Paragraph("Negotiation Suggestions", heading_style))
        for s in result.negotiation_suggestions:
            story.append(Paragraph(s.clause_name.replace('_', ' ').title(), subheading_style))
            story.append(Paragraph(f"<b>Original:</b> {s.original_text[:400]}", normal_style))
            story.append(Paragraph(f"<b>Suggested:</b> {s.suggested_text}", normal_style))
            story.append(Paragraph(f"<b>Why Better:</b> {s.negotiation_rationale}", normal_style))
            for tactic in s.negotiation_tactics:
                story.append(Paragraph(f"• {tactic}", normal_style))
            story.append(Spacer(1, 8))
    doc.build(story)
    buffer.seek(0)
    return buffer


# ---- SIDEBAR ----
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding: 20px 0;">
        <div style="font-size:3em;">⚖️</div>
        <div style="font-family:'Playfair Display',serif; font-size:1.4em; font-weight:700;
                    background:linear-gradient(135deg,#f6d365,#fda085);
                    -webkit-background-clip:text; -webkit-text-fill-color:transparent;">
            LexAI
        </div>
        <div style="color:#64748b; font-size:0.8em; letter-spacing:2px; text-transform:uppercase;">
            Legal Intelligence
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    st.markdown("""
    <div style="color:#94a3b8; font-size:0.85em;">
        <div class="agent-step">
            <div class="agent-dot"></div>
            <span><b style="color:#f6d365;">Agent 1</b> — Clause Extractor</span>
        </div>
        <div class="agent-step">
            <div class="agent-dot"></div>
            <span><b style="color:#f6d365;">Agent 2</b> — Risk Analyst</span>
        </div>
        <div class="agent-step">
            <div class="agent-dot"></div>
            <span><b style="color:#f6d365;">Agent 3</b> — Negotiator</span>
        </div>
        <div class="agent-step">
            <div class="agent-dot"></div>
            <span><b style="color:#f6d365;">Agent 4</b> — Summarizer</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()
    st.markdown('<div style="color:#64748b; font-size:0.8em; text-align:center;">Powered by Groq · Llama 3.3 70B</div>', unsafe_allow_html=True)


# ---- HERO HEADER ----
st.markdown("""
<div class="hero-header">
    <div class="hero-title">LexAI Contract Analyzer</div>
    <div class="hero-subtitle">Multi-Agent Legal Intelligence System</div>
</div>
""", unsafe_allow_html=True)

st.divider()

# ---- INPUT SECTION ----
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.markdown('<div style="color:#f6d365; font-weight:600; margin-bottom:8px;">📎 Upload Contract</div>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Upload", type=["pdf", "txt"], label_visibility="collapsed")

with col2:
    st.markdown('<div style="color:#f6d365; font-weight:600; margin-bottom:8px;">✏️ Or Paste Contract Text</div>', unsafe_allow_html=True)
    pasted_text = st.text_area("Paste", height=160, placeholder="Paste your contract text here...", label_visibility="collapsed")

contract_text = ""

if uploaded_file is not None:
    with st.spinner(f"📄 Reading {uploaded_file.name}..."):
        file_bytes = uploaded_file.read()
        if uploaded_file.name.endswith(".pdf"):
            raw_text = extract_text_from_pdf(file_bytes)
        else:
            raw_text = file_bytes.decode("utf-8", errors="replace")
        contract_text = clean_contract_text(raw_text)
    if contract_text:
        st.markdown(f'<div style="color:#16a34a; padding:10px; background:rgba(22,163,74,0.1); border-radius:8px; border:1px solid rgba(22,163,74,0.3);">✅ Extracted {len(contract_text):,} characters from {uploaded_file.name}</div>', unsafe_allow_html=True)
    else:
        st.error("❌ Could not extract text. Try pasting directly.")
elif pasted_text.strip():
    contract_text = pasted_text.strip()

st.divider()

# ---- ANALYZE BUTTON ----
analyze_btn = st.button(
    "⚡ ANALYZE CONTRACT",
    disabled=not bool(contract_text),
    use_container_width=True,
)

if not contract_text:
    st.markdown('<div style="text-align:center; color:#475569; padding:20px;">👆 Upload a file or paste contract text above to begin</div>', unsafe_allow_html=True)


# ---- PIPELINE ----
if analyze_btn and contract_text:
    pipeline = get_pipeline()

    # Animated progress steps
    progress_placeholder = st.empty()
    with progress_placeholder.container():
        st.markdown("""
        <div class="premium-card">
            <div style="color:#f6d365; font-weight:700; font-size:1.1em; margin-bottom:16px;">🤖 Running Multi-Agent Analysis...</div>
        </div>
        """, unsafe_allow_html=True)

    steps = [
        ("📄", "Extractor Agent", "Identifying key clauses..."),
        ("🔍", "Risk Analyst Agent", "Scoring legal risks..."),
        ("🤝", "Negotiator Agent", "Generating alternatives..."),
        ("📝", "Summarizer Agent", "Writing plain English summary..."),
    ]

    progress = st.progress(0)
    status = st.empty()

    start_time = time.time()

    for i, (emoji, name, desc) in enumerate(steps):
        status.markdown(f'<div style="color:#94a3b8; text-align:center;">{emoji} <b style="color:#f6d365;">{name}</b> — {desc}</div>', unsafe_allow_html=True)
        progress.progress((i + 1) * 20)
        if i == 0:
            result = get_pipeline().run(contract_text)
        time.sleep(0.3)

    progress.progress(100)
    progress_placeholder.empty()

    elapsed = time.time() - start_time

    st.markdown(f"""
    <div class="premium-card" style="text-align:center; border-color:rgba(22,163,74,0.4);">
        <div style="font-size:2em;">✅</div>
        <div style="color:#16a34a; font-weight:700; font-size:1.2em;">Analysis Complete</div>
        <div style="color:#64748b;">{elapsed:.1f} seconds · 4 agents · {len(result.extracted_clauses or {})} clauses found</div>
    </div>
    """, unsafe_allow_html=True)

    if result.errors:
        with st.expander(f"⚠️ {len(result.errors)} non-fatal error(s)"):
            for err in result.errors:
                st.warning(err)

    # ---- DOWNLOAD BUTTON ----
    st.markdown("###")
    pdf_buffer = generate_pdf_report(result)
    st.download_button(
        label="📥 Download Full Report as PDF",
        data=pdf_buffer,
        file_name="lexai_legal_report.pdf",
        mime="application/pdf",
        use_container_width=True,
    )

    st.divider()

    # ---- TABS ----
    tab1, tab2, tab3, tab4 = st.tabs(["📄 Clauses", "🔍 Risk Analysis", "🤝 Negotiation", "📝 Summary"])

    # ---- TAB 1: CLAUSES ----
    with tab1:
        st.markdown('<div style="color:#f6d365; font-size:1.3em; font-weight:700; margin-bottom:16px;">Extracted Clauses</div>', unsafe_allow_html=True)
        if result.extracted_clauses:
            for clause_name, clause_text in result.extracted_clauses.items():
                if clause_name.startswith("_"):
                    continue
                with st.expander(f"📋 {clause_name.replace('_', ' ').title()}"):
                    if clause_text in ("NOT FOUND", "EXTRACTION_FAILED"):
                        st.markdown(f'<div style="color:#64748b; font-style:italic;">⚠️ {clause_text} — Not detected in this contract</div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="clause-original">{clause_text}</div>', unsafe_allow_html=True)

    # ---- TAB 2: RISK ----
    with tab2:
        st.markdown('<div style="color:#f6d365; font-size:1.3em; font-weight:700; margin-bottom:16px;">Risk Analysis</div>', unsafe_allow_html=True)
        if result.risk_assessments:
            avg_score = sum(r.risk_score for r in result.risk_assessments) / len(result.risk_assessments)
            max_score = max(r.risk_score for r in result.risk_assessments)

            col_a, col_b, col_c = st.columns(3)
            col_a.metric("⚡ Average Risk", f"{avg_score:.1f} / 10")
            col_b.metric("🔴 Highest Risk", f"{max_score} / 10")
            col_c.metric("📊 Clauses", len(result.risk_assessments))

            st.divider()

            for risk in result.risk_assessments:
                level, label, color = get_risk_info(risk.risk_score)
                with st.expander(f"{risk_emoji(risk.risk_score)} {risk.clause_name.replace('_', ' ').title()} — {risk.risk_score}/10"):
                    col_score, col_info = st.columns([1, 4])
                    with col_score:
                        st.markdown(f'<div class="score-circle score-{level}">{risk.risk_score}</div>', unsafe_allow_html=True)
                    with col_info:
                        st.markdown(f'<span class="risk-badge-{level}">{label}</span>', unsafe_allow_html=True)
                        st.markdown(render_risk_bar(risk.risk_score), unsafe_allow_html=True)
                        st.markdown(f'<div style="color:#94a3b8; margin-top:8px;">{risk.risk_explanation}</div>', unsafe_allow_html=True)
                    st.markdown("**Risk Factors:**")
                    for factor in risk.risk_factors:
                        st.markdown(f'<div style="color:#94a3b8; padding:4px 0;">• {factor}</div>', unsafe_allow_html=True)

    # ---- TAB 3: NEGOTIATION ----
    with tab3:
        st.markdown('<div style="color:#f6d365; font-size:1.3em; font-weight:700; margin-bottom:16px;">Negotiation Suggestions</div>', unsafe_allow_html=True)
        if result.negotiation_suggestions:
            for suggestion in result.negotiation_suggestions:
                with st.expander(f"🤝 {suggestion.clause_name.replace('_', ' ').title()}"):
                    col_orig, col_new = st.columns(2, gap="medium")
                    with col_orig:
                        st.markdown('<div style="color:#dc2626; font-weight:600; margin-bottom:8px;">⚠️ Original (Risky)</div>', unsafe_allow_html=True)
                        st.markdown(f'<div class="clause-original">{suggestion.original_text[:500]}</div>', unsafe_allow_html=True)
                    with col_new:
                        st.markdown('<div style="color:#2563eb; font-weight:600; margin-bottom:8px;">✅ Suggested Alternative</div>', unsafe_allow_html=True)
                        st.markdown(f'<div class="clause-suggested">{suggestion.suggested_text}</div>', unsafe_allow_html=True)
                    st.markdown("###")
                    st.markdown(f'<div style="background:rgba(37,99,235,0.08); border:1px solid rgba(37,99,235,0.2); border-radius:10px; padding:14px; color:#94a3b8;"><b style="color:#f6d365;">💡 Why This Is Better:</b><br>{suggestion.negotiation_rationale}</div>', unsafe_allow_html=True)
                    st.markdown("###")
                    st.markdown('<div style="color:#f6d365; font-weight:600;">🎯 Negotiation Tactics:</div>', unsafe_allow_html=True)
                    for tactic in suggestion.negotiation_tactics:
                        st.markdown(f'<div style="color:#94a3b8; padding:6px 0; border-bottom:1px solid rgba(246,211,101,0.08);">→ {tactic}</div>', unsafe_allow_html=True)
        elif result.risk_assessments is not None:
            st.markdown('<div class="premium-card" style="text-align:center; color:#16a34a;">✅ No high-risk clauses detected — contract looks balanced!</div>', unsafe_allow_html=True)

    # ---- TAB 4: SUMMARY ----
    with tab4:
        st.markdown('<div style="color:#f6d365; font-size:1.3em; font-weight:700; margin-bottom:16px;">Plain English Summary</div>', unsafe_allow_html=True)
        st.markdown('<div style="color:#64748b; margin-bottom:20px; font-style:italic;">What this contract really means for you — no legal jargon</div>', unsafe_allow_html=True)
        if result.plain_english_summary:
            st.markdown(f'<div class="summary-box">{result.plain_english_summary}</div>', unsafe_allow_html=True)
        else:
            st.warning("Summary not generated.")