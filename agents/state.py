from typing import Optional
from pydantic import BaseModel, Field

class ClauseRisk(BaseModel):
    clause_name: str
    original_text: str
    risk_score: int
    risk_explanation: str
    risk_factors: list[str]

class NegotiationSuggestion(BaseModel):
    clause_name: str
    original_text: str
    suggested_text: str
    negotiation_rationale: str
    negotiation_tactics: list[str]

class AgentState(BaseModel):
    contract_text: str = Field(description="The raw contract text to analyze")
    extracted_clauses: Optional[dict[str, str]] = Field(default=None)
    risk_assessments: Optional[list[ClauseRisk]] = Field(default=None)
    negotiation_suggestions: Optional[list[NegotiationSuggestion]] = Field(default=None)
    plain_english_summary: Optional[str] = Field(default=None)
    pipeline_start_time: Optional[str] = Field(default=None)
    errors: list[str] = Field(default_factory=list)

    def add_error(self, agent_name: str, error: str):
        self.errors.append(f"[{agent_name}] {error}")

    def is_complete(self):
        return all([
            self.extracted_clauses is not None,
            self.risk_assessments is not None,
            self.negotiation_suggestions is not None,
            self.plain_english_summary is not None,
        ])