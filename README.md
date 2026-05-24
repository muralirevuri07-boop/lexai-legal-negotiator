<div align="center">



\# ⚖️ LexAI — Legal Clause Negotiator



\### AI-Powered Multi-Agent Contract Analysis System



\[!\[Live Demo](https://img.shields.io/badge/🚀\_Live\_Demo-lexai--legal--negotiator.streamlit.app-f6d365?style=for-the-badge)](https://lexai-legal-negotiator.streamlit.app)

\[!\[Python](https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge\&logo=python)](https://python.org)

\[!\[LangChain](https://img.shields.io/badge/LangChain-0.3-green?style=for-the-badge)](https://langchain.com)

\[!\[Groq](https://img.shields.io/badge/Groq-Llama\_3.3\_70B-orange?style=for-the-badge)](https://groq.com)

\[!\[Streamlit](https://img.shields.io/badge/Streamlit-1.45-red?style=for-the-badge)](https://streamlit.io)



\*\*What lawyers charge $2,000 for — LexAI does in 42 seconds. For free.\*\*



\[🚀 Try It Live](https://lexai-legal-negotiator.streamlit.app) · \[📽️ Demo Video](#) · \[⭐ Star this repo](#)



</div>



\---



\## 🤯 What Is This?



LexAI is a \*\*multi-agent AI system\*\* that analyzes legal contracts and protects you from unfair clauses — instantly.



Upload any contract (NDA, employment, freelance, service agreement) and get:



\- 📄 \*\*Extracted clauses\*\* — every key legal section identified

\- 🔴 \*\*Risk scores\*\* — each clause scored 1-10 for danger

\- 🤝 \*\*Negotiation suggestions\*\* — fairer alternative wording

\- 📝 \*\*Plain English summary\*\* — what it really means for YOU

\- 📥 \*\*PDF report\*\* — professional downloadable report



\---



\## 🤖 How It Works — 4 Agent Pipeline



Contract Text / PDF

│

▼

┌───────────────────┐

│  Agent 1          │  Groq / Llama 3.3 70B

│  EXTRACTOR        │  → Identifies 8 key clause types

└────────┬──────────┘

│

▼

┌───────────────────┐

│  Agent 2          │  Groq / Llama 3.3 70B

│  RISK ANALYST     │  → Scores each clause 1-10

└────────┬──────────┘

│

▼

┌───────────────────┐

│  Agent 3          │  Groq / Llama 3.3 70B

│  NEGOTIATOR       │  → Suggests fairer alternatives

└────────┬──────────┘

│

▼

┌───────────────────┐

│  Agent 4          │  Groq / Llama 3.3 70B

│  SUMMARIZER       │  → Plain English summary

└───────────────────┘

│

▼

📥 PDF Report



\---



\## 🚨 Real Example — What LexAI Catches



| Clause | Risk | What It Found |

|---|---|---|

| Dispute Resolution | 🔴 10/10 | Arbitrator chosen solely by company — RIGGED |

| Indemnification | 🔴 9/10 | Unlimited liability — DANGEROUS |

| Intellectual Property | 🔴 9/10 | Your personal ideas belong to them — THEFT |

| Termination | 🔴 8/10 | Fire you instantly, you need 90 days notice — UNFAIR |

| Payment Terms | 🟠 7/10 | They can cut your salary anytime — ILLEGAL in many countries |



\---



\## ⚡ Tech Stack



| Technology | Purpose |

|---|---|

| 🦜 LangChain | Agent orchestration |

| ⚡ Groq API | Ultra-fast LLM inference |

| 🦙 Llama 3.3 70B | Legal reasoning \& analysis |

| 🎨 Streamlit | Premium dark UI |

| 📄 ReportLab | PDF report generation |

| 🐍 Python 3.11 | Core language |



\---



\## 🏗️ Project Structure

lexai-legal-negotiator/

├── app.py                    # Streamlit UI (premium dark theme)

├── pipeline.py               # Agent orchestrator

├── requirements.txt          # Dependencies

├── agents/

│   ├── extractor\_agent.py    # Clause extraction

│   ├── risk\_analyst\_agent.py # Risk scoring

│   ├── negotiator\_agent.py   # Negotiation suggestions

│   ├── summarizer\_agent.py   # Plain English summary

│   ├── base\_agent.py         # Base class + retry logic

│   └── state.py              # Shared pipeline state

├── config/

│   └── settings.py           # Environment configuration

└── utils/

├── document\_parser.py    # PDF text extraction

└── logger.py             # Logging setup



\---



\## 🚀 Run Locally



```bash

\# Clone the repo

git clone https://github.com/muralirevuri07-boop/lexai-legal-negotiator.git

cd lexai-legal-negotiator



\# Create virtual environment

python -m venv venv

venv\\Scripts\\activate  # Windows

source venv/bin/activate  # Mac/Linux



\# Install dependencies

pip install -r requirements.txt



\# Add your API keys

cp .env.example .env

\# Edit .env and add GROQ\_API\_KEY and GOOGLE\_API\_KEY



\# Run the app

streamlit run app.py

```



\---



\## 🔑 Environment Variables



```env

GROQ\_API\_KEY=your\_groq\_api\_key

GOOGLE\_API\_KEY=your\_google\_api\_key

GROQ\_MODEL=llama-3.3-70b-versatile

GEMINI\_MODEL=gemini-2.0-flash

```



Get your free API keys:

\- 🔑 \[Groq API Key](https://console.groq.com/keys) — Free

\- 🔑 \[Google Gemini Key](https://aistudio.google.com/app/apikey) — Free



\---



\## 💡 Key Design Decisions



| Decision | Why |

|---|---|

| Sequential agent pipeline | Clear data flow, easy to debug |

| Shared Pydantic state | Type-safe data passing between agents |

| Non-fatal error handling | Partial results better than total failure |

| Groq for speed | 42 second analysis vs minutes on other APIs |

| ReportLab PDF | Professional reports users can share |



\---



\## 🗺️ Roadmap



\- \[ ] Chat with your contract (ask questions)

\- \[ ] Compare two contracts side by side

\- \[ ] Support for more languages

\- \[ ] Stripe payment integration

\- \[ ] Contract history \& saved analyses

\- \[ ] API endpoint for developers



\---



\## 🙏 Built With



\- \[LangChain](https://langchain.com) — Agent framework

\- \[Groq](https://groq.com) — Lightning fast inference

\- \[Streamlit](https://streamlit.io) — UI framework

\- \[Meta Llama 3.3](https://llama.meta.com) — The brain



\---



<div align="center">



\*\*If this saved you from a bad contract, give it a ⭐\*\*



Built with ❤️ by \[Murali](https://github.com/muralirevuri07-boop)



\[🚀 Try LexAI Live](https://lexai-legal-negotiator.streamlit.app)

