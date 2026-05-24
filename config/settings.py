import os
from dotenv import load_dotenv
load_dotenv()

class Settings:
    @property
    def groq_api_key(self):
        return os.getenv("GROQ_API_KEY", "")
    @property
    def google_api_key(self):
        return os.getenv("GOOGLE_API_KEY", "")
    @property
    def groq_model(self):
        return os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    @property
    def gemini_model(self):
        return os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
    @property
    def extractor_max_tokens(self):
        return int(os.getenv("EXTRACTOR_MAX_TOKENS", "2000"))
    @property
    def risk_analyst_max_tokens(self):
        return int(os.getenv("RISK_ANALYST_MAX_TOKENS", "2000"))
    @property
    def negotiator_max_tokens(self):
        return int(os.getenv("NEGOTIATOR_MAX_TOKENS", "3000"))
    @property
    def summarizer_max_tokens(self):
        return int(os.getenv("SUMMARIZER_MAX_TOKENS", "800"))
    @property
    def extractor_temperature(self):
        return float(os.getenv("EXTRACTOR_TEMPERATURE", "0.1"))
    @property
    def risk_analyst_temperature(self):
        return float(os.getenv("RISK_ANALYST_TEMPERATURE", "0.2"))
    @property
    def negotiator_temperature(self):
        return float(os.getenv("NEGOTIATOR_TEMPERATURE", "0.7"))
    @property
    def summarizer_temperature(self):
        return float(os.getenv("SUMMARIZER_TEMPERATURE", "0.3"))
    @property
    def log_level(self):
        return os.getenv("LOG_LEVEL", "INFO")
    @property
    def log_file(self):
        return os.getenv("LOG_FILE", "logs/legal_negotiator.log")

settings = Settings()