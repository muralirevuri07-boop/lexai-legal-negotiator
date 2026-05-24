from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from agents.base_agent import BaseAgent
from agents.state import AgentState
from config.settings import settings
from utils.logger import app_logger

SYSTEM_PROMPT = """You are a plain-language legal translator.
Explain contract analysis results to a busy business person who is NOT a lawyer.
Write exactly ONE paragraph (4-6 sentences) covering:
1. What type of contract this is
2. The most important risks found
3. What needs negotiation and why it matters
4. A clear recommendation: safe to sign / negotiate first / do not sign
Use plain English, no legal jargon, be direct and actionable."""

HUMAN_PROMPT_TEMPLATE = """Here is the full contract analysis:

EXTRACTED CLAUSES:
{clauses_summary}

RISK FINDINGS:
{risk_summary}

NEGOTIATION SUGGESTIONS:
{negotiation_summary}

Write the plain English summary paragraph now:"""

class SummarizerAgent(BaseAgent):

    @property
    def name(self):
        return "SummarizerAgent"

    def __init__(self):
        self.llm = ChatGroq(
            api_key=settings.groq_api_key,
            model=settings.groq_model,
            temperature=settings.summarizer_temperature,
            max_tokens=settings.summarizer_max_tokens,
        )

    def _execute(self, state: AgentState) -> AgentState:
        clauses_summary = self._summarize_clauses(state)
        risk_summary = self._summarize_risks(state)
        negotiation_summary = self._summarize_negotiations(state)

        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=HUMAN_PROMPT_TEMPLATE.format(
                clauses_summary=clauses_summary,
                risk_summary=risk_summary,
                negotiation_summary=negotiation_summary,
            )),
        ]

        response = self.llm.invoke(messages)
        state.plain_english_summary = response.content.strip()
        return state

    def _summarize_clauses(self, state):
        if not state.extracted_clauses:
            return "No clauses were extracted."
        found = [k for k, v in state.extracted_clauses.items() if v not in ("NOT FOUND", "EXTRACTION_FAILED")]
        missing = [k for k, v in state.extracted_clauses.items() if v == "NOT FOUND"]
        lines = [f"Found: {', '.join(found)}"]
        if missing:
            lines.append(f"Missing: {', '.join(missing)}")
        return "\n".join(lines)

    def _summarize_risks(self, state):
        if not state.risk_assessments:
            return "No risk analysis available."
        lines = []
        for r in state.risk_assessments:
            lines.append(f"- {r.clause_name} (score {r.risk_score}/10): {r.risk_explanation[:200]}")
        return "\n".join(lines)

    def _summarize_negotiations(self, state):
        if not state.negotiation_suggestions:
            return "No negotiation suggestions."
        lines = []
        for s in state.negotiation_suggestions:
            lines.append(f"- {s.clause_name}: {s.negotiation_rationale[:200]}")
        return "\n".join(lines)