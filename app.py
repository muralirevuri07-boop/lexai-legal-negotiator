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
    page_title="Legal Clause Negotiator",
    page_icon="⚖️",
    layout="wide",
)

st.markdown("""
<style>
.risk-critical { background:#fee2e2; border-left:4px solid #dc2626; padding:10px; border-radius:4px; }
.risk-high { background:#fef3c7; border-left:4px solid #d97706; padding:10px; border-radius:4px; }
.risk-medium { background:#fefce8; border-left:4px solid #ca8a04; padding:10px; border-radius:4px; }
.risk-low { background:#f0fdf4; border-left:4px solid #16a34a; padding:10px; border-radius:4px; }
.clause-box { background:#f8fafc; border:1px solid #e2e8f0; padding:12px; border-radius:6px; font-family:monospace; font-size:0.85em; }
.suggestion-box { background:#eff6ff; border:1px solid #bfdbfe; padding:12px; border-radius:6px; }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def get_pipeline():
    return LegalNegotiatorPipeline()

def risk_css_class(score):
    if score >= 8: return "risk-critical"
    if score >= 6: return "risk-high"
    if score >= 4: return "risk-medium"
    return "risk-low"

def risk_emoji(score):
    if score >= 8: return "🔴"
    if score >= 6: return "🟠"
    if score >= 4: return "🟡"
    return "🟢"

def generate_pdf_report(result):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                            rightMargin=inch, leftMargin=inch,
                            topMargin=inch, bottomMargin=inch)
    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle('CustomTitle', parent=styles['Title'],
                                  fontSize=24, textColor=colors.HexColor('#1e3a5f'),
                                  spaceAfter=6)
    heading_style = ParagraphStyle('CustomHeading', parent=styles['Heading1'],
                                    fontSize=14, textColor=colors.HexColor('#1e3a5f'),
                                    spaceBefore=16, spaceAfter=6)
    subheading_style = ParagraphStyle('CustomSubHeading', parent=styles['Heading2'],
                                       fontSize=12, textColor=colors.HexColor('#2563eb'),
                                       spaceBefore=10, spaceAfter=4)
    normal_style = ParagraphStyle('CustomNormal', parent=styles['Normal'],
                                   fontSize=10, spaceAfter=6, leading=14)
    risk_style = ParagraphStyle('RiskStyle', parent=styles['Normal'],
                                 fontSize=10, spaceAfter=4, leading=14,
                                 textColor=colors.HexColor('#dc2626'))

    story = []

    # Title
    story.append(Paragraph("⚖️ Legal Clause Negotiator", title_style))
    story.append(Paragraph("Contract Analysis Report", styles['Heading2']))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#1e3a5f')))
    story.append(Spacer(1, 12))

    # Executive Summary
    story.append(Paragraph("📋 Executive Summary", heading_style))
    if result.plain_english_summary:
        story.append(Paragraph(result.plain_english_summary, normal_style))
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#e2e8f0')))

    # Risk Overview Table
    if result.risk_assessments:
        story.append(Paragraph("🔍 Risk Overview", heading_style))
        avg_score = sum(r.risk_score for r in result.risk_assessments) / len(result.risk_assessments)
        max_score = max(r.risk_score for r in result.risk_assessments)

        table_data = [['Clause', 'Risk Score', 'Risk Level']]
        for r in result.risk_assessments:
            if r.risk_score >= 8: level = "CRITICAL"
            elif r.risk_score >= 6: level = "HIGH"
            elif r.risk_score >= 4: level = "MEDIUM"
            else: level = "LOW"
            table_data.append([
                r.clause_name.replace('_', ' ').title(),
                f"{r.risk_score}/10",
                level
            ])

        table = Table(table_data, colWidths=[3*inch, 1.5*inch, 1.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1e3a5f')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 11),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#f8fafc'), colors.white]),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
            ('FONTSIZE', (0,1), (-1,-1), 10),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ]))
        story.append(table)
        story.append(Spacer(1, 6))
        story.append(Paragraph(f"Average Risk Score: {avg_score:.1f}/10  |  Highest Risk: {max_score}/10  |  Clauses Analyzed: {len(result.risk_assessments)}", normal_style))
        story.append(Spacer(1, 10))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#e2e8f0')))

    # Detailed Risk Analysis
    if result.risk_assessments:
        story.append(Paragraph("📊 Detailed Risk Analysis", heading_style))
        for r in result.risk_assessments:
            story.append(Paragraph(f"{r.clause_name.replace('_', ' ').title()} — Score: {r.risk_score}/10", subheading_style))
            story.append(Paragraph(f"<b>Risk Explanation:</b> {r.risk_explanation}", normal_style))
            for factor in r.risk_factors:
                story.append(Paragraph(f"• {factor}", normal_style))
            story.append(Spacer(1, 6))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#e2e8f0')))

    # Negotiation Suggestions
    if result.negotiation_suggestions:
        story.append(Paragraph("🤝 Negotiation Suggestions", heading_style))
        for s in result.negotiation_suggestions:
            story.append(Paragraph(s.clause_name.replace('_', ' ').title(), subheading_style))
            story.append(Paragraph("<b>Original (Risky) Text:</b>", normal_style))
            story.append(Paragraph(s.original_text[:400], ParagraphStyle('mono', parent=normal_style,
                                                                           backColor=colors.HexColor('#f8fafc'),
                                                                           borderColor=colors.HexColor('#e2e8f0'),
                                                                           borderWidth=1, borderPadding=6)))
            story.append(Spacer(1, 4))
            story.append(Paragraph("<b>Suggested Alternative:</b>", normal_style))
            story.append(Paragraph(s.suggested_text, ParagraphStyle('suggest', parent=normal_style,
                                                                      backColor=colors.HexColor('#eff6ff'),
                                                                      borderColor=colors.HexColor('#bfdbfe'),
                                                                      borderWidth=1, borderPadding=6)))
            story.append(Spacer(1, 4))
            story.append(Paragraph(f"<b>Why This Is Better:</b> {s.negotiation_rationale}", normal_style))
            story.append(Paragraph("<b>Negotiation Tactics:</b>", normal_style))
            for tactic in s.negotiation_tactics:
                story.append(Paragraph(f"• {tactic}", normal_style))
            story.append(Spacer(1, 10))

    doc.build(story)
    buffer.seek(0)
    return buffer

with st.sidebar:
    st.title("⚖️ Legal Clause Negotiator")
    st.markdown("**Multi-Agent Contract Analysis System**")
    st.divider()
    st.markdown("""
    **Pipeline:**
    1. 📄 Extractor — finds key clauses
    2. 🔍 Risk Analyst — scores each clause
    3. 🤝 Negotiator — suggests better wording
    4. 📝 Summarizer — plain English overview

    **Models:**
    - Agents 1, 2, 3, 4 → Groq (Llama 3.3 70B)
    """)

st.header("⚖️ Contract Analysis & Negotiation")
st.markdown("Upload a contract PDF or paste text below to begin analysis.")

col1, col2 = st.columns([1, 1])

with col1:
    uploaded_file = st.file_uploader("📎 Upload Contract (PDF or TXT)", type=["pdf", "txt"])

with col2:
    st.markdown("**Or paste contract text directly:**")
    pasted_text = st.text_area("Contract Text", height=200, placeholder="Paste your contract text here...", label_visibility="collapsed")

contract_text = ""

if uploaded_file is not None:
    with st.spinner(f"Reading {uploaded_file.name}..."):
        file_bytes = uploaded_file.read()
        if uploaded_file.name.endswith(".pdf"):
            raw_text = extract_text_from_pdf(file_bytes)
        else:
            raw_text = file_bytes.decode("utf-8", errors="replace")
        contract_text = clean_contract_text(raw_text)
    if contract_text:
        st.success(f"✅ Extracted {len(contract_text):,} characters from {uploaded_file.name}")
    else:
        st.error("❌ Could not extract text. Try pasting directly.")
elif pasted_text.strip():
    contract_text = pasted_text.strip()

st.divider()
analyze_btn = st.button("🔍 Analyze Contract", type="primary", disabled=not bool(contract_text), use_container_width=True)

if not contract_text:
    st.info("👆 Upload a file or paste contract text above to get started.")

if analyze_btn and contract_text:
    pipeline = get_pipeline()
    with st.spinner("Running multi-agent analysis... (30-60 seconds)"):
        progress = st.progress(0, text="Starting pipeline...")
        start_time = time.time()
        try:
            progress.progress(10, text="📄 Extractor Agent running...")
            result = pipeline.run(contract_text)
            progress.progress(100, text="✅ Done!")
        except Exception as e:
            st.error(f"❌ Pipeline failed: {str(e)}")
            st.stop()

    elapsed = time.time() - start_time
    st.success(f"✅ Analysis completed in {elapsed:.1f} seconds")

    if result.errors:
        with st.expander(f"⚠️ {len(result.errors)} error(s)"):
            for err in result.errors:
                st.warning(err)

    # PDF Download Button
    st.markdown("### 📥 Download Report")
    pdf_buffer = generate_pdf_report(result)
    st.download_button(
        label="📄 Download Full Report as PDF",
        data=pdf_buffer,
        file_name="legal_analysis_report.pdf",
        mime="application/pdf",
        use_container_width=True,
    )

    st.divider()

    tab1, tab2, tab3, tab4 = st.tabs(["📄 Extracted Clauses", "🔍 Risk Analysis", "🤝 Negotiation", "📝 Summary"])

    with tab1:
        st.subheader("Extracted Clauses")
        if result.extracted_clauses:
            for clause_name, clause_text in result.extracted_clauses.items():
                if clause_name.startswith("_"):
                    continue
                with st.expander(f"📋 {clause_name.replace('_', ' ').title()}"):
                    if clause_text in ("NOT FOUND", "EXTRACTION_FAILED"):
                        st.warning(f"⚠️ {clause_text}")
                    else:
                        st.markdown(f'<div class="clause-box">{clause_text}</div>', unsafe_allow_html=True)

    with tab2:
        st.subheader("Risk Analysis")
        if result.risk_assessments:
            avg_score = sum(r.risk_score for r in result.risk_assessments) / len(result.risk_assessments)
            col_a, col_b, col_c = st.columns(3)
            col_a.metric("Average Risk Score", f"{avg_score:.1f} / 10")
            col_b.metric("Highest Risk", f"{max(r.risk_score for r in result.risk_assessments)} / 10")
            col_c.metric("Clauses Analyzed", len(result.risk_assessments))
            st.divider()
            for risk in result.risk_assessments:
                with st.expander(f"{risk_emoji(risk.risk_score)} {risk.clause_name.replace('_', ' ').title()} — {risk.risk_score}/10"):
                    st.markdown(f'<div class="{risk_css_class(risk.risk_score)}"><strong>Risk Score: {risk.risk_score}/10</strong><br>{risk.risk_explanation}</div>', unsafe_allow_html=True)
                    st.markdown("**Risk Factors:**")
                    for factor in risk.risk_factors:
                        st.markdown(f"- {factor}")

    with tab3:
        st.subheader("Negotiation Suggestions")
        if result.negotiation_suggestions:
            for suggestion in result.negotiation_suggestions:
                with st.expander(f"🤝 {suggestion.clause_name.replace('_', ' ').title()}"):
                    col_orig, col_new = st.columns(2)
                    with col_orig:
                        st.markdown("**Original (Risky) Text:**")
                        st.markdown(f'<div class="clause-box">{suggestion.original_text[:600]}</div>', unsafe_allow_html=True)
                    with col_new:
                        st.markdown("**Suggested Alternative:**")
                        st.markdown(f'<div class="suggestion-box">{suggestion.suggested_text}</div>', unsafe_allow_html=True)
                    st.markdown("**Why This Is Better:**")
                    st.info(suggestion.negotiation_rationale)
                    st.markdown("**Negotiation Tactics:**")
                    for tactic in suggestion.negotiation_tactics:
                        st.markdown(f"- {tactic}")
        elif result.risk_assessments is not None:
            st.success("✅ No high-risk clauses — no negotiation needed!")

    with tab4:
        st.subheader("📋 Plain English Summary")
        st.markdown("*What this contract means for you in simple terms:*")
        st.divider()
        if result.plain_english_summary:
            st.markdown(result.plain_english_summary)
        else:
            st.warning("Summary not generated.")