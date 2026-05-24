<div align="center">

# ⚖️ LexAI — Legal Clause Negotiator

### What lawyers charge $2,000 for — LexAI does in 42 seconds. For free.

[![Live App](https://img.shields.io/badge/🚀_Try_It_Live-lexai--legal--negotiator.streamlit.app-f6d365?style=for-the-badge)](https://lexai-legal-negotiator.streamlit.app)
[![Demo Video](https://img.shields.io/badge/📽️_Watch_Demo-YouTube-red?style=for-the-badge&logo=youtube)](https://youtu.be/iSPs8jPsNug)

</div>

---

## 🤯 What Is This?

LexAI is a **4-agent AI system** that reads any contract and protects you from unfair clauses — instantly.

Upload a contract and get:
- 📄 Every key clause extracted automatically
- 🔴 Risk score (1-10) for each clause
- 🤝 Fairer alternative wording suggested
- 📝 Plain English explanation — no legal jargon
- 📥 Full professional PDF report to download

---

## 🤖 4 Agent Pipeline

Contract → Agent 1 (Extract) → Agent 2 (Risk Score) → Agent 3 (Negotiate) → Agent 4 (Summarize) → PDF Report

All agents powered by **Groq + Llama 3.3 70B** — analysis completes in under 60 seconds.

---

## 🚨 Real Example — What LexAI Catches

| Clause | Risk | Finding |
|---|---|---|
| Dispute Resolution | 🔴 10/10 | Arbitrator chosen solely by company — RIGGED |
| Indemnification | 🔴 9/10 | Unlimited liability — DANGEROUS |
| Intellectual Property | 🔴 9/10 | Your personal ideas belong to them — THEFT |
| Termination | 🔴 8/10 | They fire you instantly, you need 90 days notice — UNFAIR |
| Payment Terms | 🟠 7/10 | They can cut your salary anytime — ILLEGAL in many countries |

---

## ⚡ Built With

LangChain · Groq · Llama 3.3 70B · Streamlit · Python · ReportLab

---

## 🚀 Run Locally

```bash
git clone https://github.com/muralirevuri07-boop/lexai-legal-negotiator.git
cd lexai-legal-negotiator
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
# Add GROQ_API_KEY to .env
streamlit run app.py
```

---

<div align="center">

**If this saved you from a bad contract, give it a ⭐**

Built with ❤️ by [Murali](https://github.com/muralirevuri07-boop)

</div>