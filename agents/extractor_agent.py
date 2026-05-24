import json
import re
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from agents.base_agent import BaseAgent
from agents.state import AgentState
from config.settings import settings
from utils.logger import app_logger

SYSTEM_PROMPT = """You are a senior contract lawyer.
Extract key legal clauses from the contract and return a JSON object with these exact keys:
{
  "nda_confidentiality": "...",
  "termination": "...",
  "liability_limitation": "...",
  "indemnification": "...",
  "governing_law": "...",
  "payment_terms": "...",
  "intellectual_property": "...",
  "dispute_resolution": "..."
}
If a clause is NOT present, use the value: "NOT FOUND"
Return ONLY the JSON object, no markdown, no extra text."""

HUMAN_PROMPT_TEMPLATE = """Extract all key clauses from this contract:

{contract_text}

Return the JSON now:"""

class ExtractorAgent(BaseAgent):

    @property
    def name(self):
        return "ExtractorAgent"

    def __init__(self):
        self.llm = ChatGroq(
            api_key=settings.groq_api_key,
            model=settings.groq_model,
            temperature=settings.extractor_temperature,
            max_tokens=settings.extractor_max_tokens,
        )

    def _execute(self, state: AgentState) -> AgentState:
        contract_text = state.contract_text
        if len(contract_text) > 60000:
            contract_text = contract_text[:60000] + "\n\n[TRUNCATED]"

        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=HUMAN_PROMPT_TEMPLATE.format(contract_text=contract_text)),
        ]

        response = self.llm.invoke(messages)
        raw_output = response.content
        extracted_clauses = self._parse_response(raw_output)
        state.extracted_clauses = extracted_clauses
        return state

    def _parse_response(self, raw_output):
        cleaned = re.sub(r"```(?:json)?\s*", "", raw_output).strip().replace("```", "")
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", cleaned, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group())
                except json.JSONDecodeError:
                    pass
            return {
                "nda_confidentiality": "EXTRACTION_FAILED",
                "termination": "EXTRACTION_FAILED",
                "liability_limitation": "EXTRACTION_FAILED",
                "indemnification": "EXTRACTION_FAILED",
                "governing_law": "EXTRACTION_FAILED",
                "payment_terms": "EXTRACTION_FAILED",
                "intellectual_property": "EXTRACTION_FAILED",
                "dispute_resolution": "EXTRACTION_FAILED",
            }