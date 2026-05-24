import json
import re
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from agents.base_agent import BaseAgent
from agents.state import AgentState, ClauseRisk
from config.settings import settings
from utils.logger import app_logger

SYSTEM_PROMPT = """You are a legal risk analyst.
Assess the risk of each contract clause provided.
Return a JSON array:
[
  {
    "clause_name": "...",
    "original_text": "...",
    "risk_score": 7,
    "risk_explanation": "This clause is risky because...",
    "risk_factors": ["Factor 1", "Factor 2"]
  }
]
Risk scoring: 1-2 low, 3-4 moderate, 5-6 elevated, 7-8 high, 9-10 critical.
Return ONLY the JSON array, no markdown, no extra text."""

HUMAN_PROMPT_TEMPLATE = """Analyze the risk of these contract clauses:

{clauses_json}

Return the JSON array now:"""

class RiskAnalystAgent(BaseAgent):

    @property
    def name(self):
        return "RiskAnalystAgent"

    def __init__(self):
        self.llm = ChatGroq(
            api_key=settings.groq_api_key,
            model=settings.groq_model,
            temperature=settings.risk_analyst_temperature,
            max_tokens=settings.risk_analyst_max_tokens,
        )

    def _execute(self, state: AgentState) -> AgentState:
        if not state.extracted_clauses:
            state.add_error(self.name, "No extracted clauses to analyze")
            return state

        valid_clauses = {
            k: v for k, v in state.extracted_clauses.items()
            if v not in ("NOT FOUND", "EXTRACTION_FAILED") and not k.startswith("_")
        }

        if not valid_clauses:
            state.risk_assessments = []
            return state

        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=HUMAN_PROMPT_TEMPLATE.format(
                clauses_json=json.dumps(valid_clauses, indent=2)
            )),
        ]

        response = self.llm.invoke(messages)
        risk_data = self._parse_response(response.content)

        risk_assessments = []
        for item in risk_data:
            try:
                risk = ClauseRisk(
                    clause_name=item.get("clause_name", "Unknown"),
                    original_text=item.get("original_text", ""),
                    risk_score=int(item.get("risk_score", 5)),
                    risk_explanation=item.get("risk_explanation", ""),
                    risk_factors=item.get("risk_factors", []),
                )
                risk_assessments.append(risk)
            except Exception as e:
                app_logger.warning(f"Skipping malformed risk item: {e}")

        risk_assessments.sort(key=lambda r: r.risk_score, reverse=True)
        state.risk_assessments = risk_assessments
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