from datetime import datetime, timezone
from agents.state import AgentState
from agents.extractor_agent import ExtractorAgent
from agents.risk_analyst_agent import RiskAnalystAgent
from agents.negotiator_agent import NegotiatorAgent
from agents.summarizer_agent import SummarizerAgent
from utils.logger import app_logger

class LegalNegotiatorPipeline:

    def __init__(self):
        app_logger.info("Initializing Legal Negotiator Pipeline...")
        self.agents = [
            ExtractorAgent(),
            RiskAnalystAgent(),
            NegotiatorAgent(),
            SummarizerAgent(),
        ]
        app_logger.info(f"Pipeline ready with {len(self.agents)} agents")

    def run(self, contract_text: str) -> AgentState:
        if not contract_text or not contract_text.strip():
            raise ValueError("Contract text cannot be empty")

        state = AgentState(
            contract_text=contract_text,
            pipeline_start_time=datetime.now(timezone.utc).isoformat(),
        )

        app_logger.info("PIPELINE STARTED")
        app_logger.info(f"Contract length: {len(contract_text):,} characters")

        for agent in self.agents:
            state = agent.run(state)

        app_logger.info(f"PIPELINE COMPLETE — errors: {len(state.errors)}")
        return state