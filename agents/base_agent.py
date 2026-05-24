import time
from abc import ABC, abstractmethod
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from agents.state import AgentState
from utils.logger import app_logger

class BaseAgent(ABC):

    @property
    @abstractmethod
    def name(self):
        ...

    @abstractmethod
    def _execute(self, state: AgentState) -> AgentState:
        ...

    def run(self, state: AgentState) -> AgentState:
        app_logger.info(f"Starting {self.name}")
        start = time.time()
        try:
            state = self._execute_with_retry(state)
            elapsed = time.time() - start
            app_logger.info(f"{self.name} completed in {elapsed:.2f}s")
        except Exception as e:
            elapsed = time.time() - start
            error_msg = f"{type(e).__name__}: {str(e)}"
            app_logger.error(f"{self.name} failed after {elapsed:.2f}s — {error_msg}")
            state.add_error(self.name, error_msg)
        return state

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((ConnectionError, TimeoutError)),
    )
    def _execute_with_retry(self, state: AgentState) -> AgentState:
        return self._execute(state)