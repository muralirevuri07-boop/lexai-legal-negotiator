import json
import re
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from agents.base_agent import BaseAgent
from agents.state import AgentState, NegotiationSuggestion
from config.settings import settings
from utils.logger import app_logger

SYSTEM_PROMPT = """You are a senior contract negotiator.
Suggest fairer alternative language for risky clauses.
Return a JSON array:
[
  {
    "clause_name": "...",
    "original_text": "...",
    "suggested_text": "...",
    "negotiation_rationale": "Why this is better...",
    "negotiation_tactics": ["Tactic 1", "Tactic 2", "Tactic 3"]
  }
]
Only suggest changes for clauses with risk_score >= 5.
Return ONLY the JSON array, no markdown, no extra text."""

HUMAN_PROMPT_TEMPLATE = """Suggest fairer alternative language for these risky clauses:

{risk_json}

Return the JSON array now:"""

class NegotiatorAgent(BaseAgent):

    @property
    def name(self):
        return "NegotiatorAgent"

    def __init__(self):
        self.llm = ChatGroq(
            api_key=settings.groq_api_key,
            model=settings.groq_model,
            temperature=settings.negotiator_temperature,
            max_tokens=settings.negotiator_max_tokens,
        )

    def _execute(self, state: AgentState) -> AgentState:
        if not state.risk_assessments:
            state.add_error(self.name, "No risk assessments to negotiate")
            return state

        high_risk = [r for r in state.risk_assessments if r.risk_score >= 5]

        if not high_risk:
            state.negotiation_suggestions = []
            return state

        risk_data = [
            {
                "clause_name": r.clause_name,
                "original_text": r.original_text,
                "risk_score": r.risk_score,
                "risk_explanation": r.risk_explanation,
                "risk_factors": r.risk_factors,
            }
            for r in high_risk
        ]

        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=HUMAN_PROMPT_TEMPLATE.format(
                risk_json=json.dumps(risk_data, indent=2)
            )),
        ]

        response = self.llm.invoke(messages)
        raw_output = response.content
        suggestions_data = self._parse_response(raw_output)

        suggestions = []
        for item in suggestions_data:
            try:
                suggestion = NegotiationSuggestion(
                    clause_name=item.get("clause_name", "Unknown"),
                    original_text=item.get("original_text", ""),
                    suggested_text=item.get("suggested_text", ""),
                    negotiation_rationale=item.get("negotiation_rationale", ""),
                    negotiation_tactics=item.get("negotiation_tactics", []),
                )
                suggestions.append(suggestion)
            except Exception as e:
                app_logger.warning(f"Skipping malformed suggestion: {e}")

        state.negotiation_suggestions = suggestions
        return state

    def _parse_response(self, raw_output):
        cleaned = re.sub(r"```(?:json)?\s*", "", raw_output).strip().replace("```", "")
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            match = re.search(r"\[.*\]", cleaned, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group())
                except json.JSONDecodeError:
                    pass
            return []