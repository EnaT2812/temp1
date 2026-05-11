# Banking AI-Agents

> **Course:** Applications of Natural Language Processing in Industry – Project 3  
> **Lecturer:** Dr. Nguyen Hong Buu Long  
> **University:** VNUHCM – University of Science, Faculty of Information Technology

---

## Overview

A complete **AI agentic pipeline** for banking customer support built with **FastAPI** and **Ollama** (`gpt-oss:20b`).  
The system receives a customer message and routes it through six sequential nodes:

```
Customer Message
      │
      ▼
┌─────────────────────┐
│  1. Intent Detection │  ← fine-tuned model (Lab 2) or keyword fallback
└──────────┬──────────┘
           │
           ▼
┌─────────────────────────┐
│  2. Priority Detection   │  ← rule-based (LOW / MEDIUM / HIGH)
└──────────┬──────────────┘
           │
           ▼
┌─────────────────────┐
│  3. Policy Retrieval │  ← maps intent → FAQ/policy snippet
└──────────┬──────────┘
           │
           ▼
┌──────────────────────┐
│  4. Response Drafting │  ← Ollama gpt-oss:20b (LLM)
└──────────┬───────────┘
           │
           ▼
┌────────────────┐
│  5. Validation │  ← length, confidence, safety, missing-info checks
└──────────┬─────┘
           │
           ▼
┌───────────────────────────────────┐
│  6. Routing / Escalation          │
│  ┌──────────┐  ┌──────────────┐  │
│  │SEND_REPLY│  │ASK_MORE_INFO │  │
│  └──────────┘  └──────────────┘  │
│        ┌───────────────┐          │
│        │   ESCALATE    │          │
│        └───────────────┘          │
└───────────────────────────────────┘
```

---

## Project Structure

```
banking-agentic/
├── README.md
├── requirements.txt
├── run.py                          # Entry point → starts FastAPI server
├── .env.example                    # Environment variable template
├── app/
│   ├── main.py                     # FastAPI app factory & routes
│   ├── core/
│   │   ├── settings.py             # Pydantic-settings config (env-based)
│   │   └── schemas.py              # All Pydantic request/response schemas
│   ├── data/
│   │   └── policies.py             # Simulated FAQ/policy store (16 intents)
│   ├── clients/
│   │   ├── base.py                 # Abstract LLM client interface
│   │   └── ollama_client.py        # Ollama HTTP client implementation
│   ├── nodes/
│   │   ├── intent_node.py          # Intent detection (fine-tuned / keyword)
│   │   ├── priority_node.py        # Priority / risk classification
│   │   ├── policy_node.py          # Policy retrieval
│   │   ├── draft_node.py           # LLM response drafting
│   │   ├── validation_node.py      # Response validation checks
│   │   └── router_node.py          # Routing / escalation decision
│   └── agent/
│       └── orchestrator.py         # Main pipeline controller
└── examples/
    └── sample_requests.json        # 15 example customer requests
```

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/banking-agentic.git
cd banking-agentic
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment

```bash
cp .env.example .env
# Edit .env with your settings (Ollama URL, model name, etc.)
```

### 5. (Optional) Fine-tuned intent model from Lab 2

Place your saved HuggingFace checkpoint directory at the path specified in `INTENT_MODEL_PATH` (default: `intent_model_checkpoint/`).  
If the path does not exist, the system automatically falls back to a keyword-based classifier.

---

## Running the Server

### Option A – Local Ollama

```bash
# In a separate terminal, start Ollama and pull the model
ollama serve
ollama pull gpt-oss:20b

# Start the API server
python run.py
```

The API will be available at **http://localhost:8000**.  
Interactive docs: **http://localhost:8000/docs**

### Option B – Google Colab + Pinggy (remote LLM)

1. Run the provided **Ollama-Pinggy.ipynb** notebook on Google Colab to start Ollama and obtain a public Pinggy URL.
2. Update your `.env`:
   ```
   OLLAMA_BASE_URL=http://<your-token>.a.free.pinggy.link
   ```
3. Start the FastAPI server locally:
   ```bash
   python run.py
   ```

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/` | Health check |
| `GET` | `/health` | Ollama connectivity status |
| `POST` | `/process` | Run the full agentic pipeline |
| `GET` | `/intents` | List all supported intents |
| `GET` | `/docs` | Swagger UI |

### Example request

```bash
curl -X POST http://localhost:8000/process \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I transferred money to a wrong account number by mistake. Please help me recover my funds.",
    "customer_id": "CUST-001",
    "channel": "web"
  }'
```

### Example response (abbreviated)

```json
{
  "intent": "wrong_transfer",
  "priority": "high",
  "policy_snippet": "[Erroneous / Wrong-Account Transfer Policy] If funds were sent...",
  "draft_reply": "Dear customer, we understand this is a stressful situation...",
  "validation_passed": false,
  "routing_action": "escalate",
  "final_reply": "Your case has been escalated to a dedicated support specialist who will contact you within 1 business hour.",
  "trace": [...]
}
```

---

## Testing with Sample Requests

```bash
# Run all 15 sample requests and print results
python -c "
import json, requests
samples = json.load(open('examples/sample_requests.json'))
for s in samples:
    r = requests.post('http://localhost:8000/process', json={
        'message': s['message'],
        'customer_id': s['customer_id'],
        'channel': s['channel']
    })
    data = r.json()
    print(f\"[{s['id']}] intent={data['intent']}  priority={data['priority']}  action={data['routing_action']}\")
"
```

---

## Supported Intents (16 total)

| Intent | Policy Title |
|--------|-------------|
| `card_not_received` | Replacement / New Card Delivery Policy |
| `card_blocked` | Unblocking a Blocked Debit / Credit Card |
| `account_blocked` | Account Suspension and Reactivation Policy |
| `lost_or_stolen_card` | Lost or Stolen Card Reporting Policy |
| `transfer_failure` | Failed / Pending Transfer Resolution Policy |
| `wrong_transfer` | Erroneous / Wrong-Account Transfer Policy |
| `bill_payment_issue` | Bill Payment Failure / Duplicate Payment Policy |
| `loan_inquiry` | Personal / Home Loan Inquiry Policy |
| `loan_repayment_issue` | Loan Repayment Failure / Overdue Policy |
| `deposit_issue` | Cash / Cheque Deposit Not Credited Policy |
| `interest_rate_inquiry` | Savings / Fixed Deposit Interest Rate Information |
| `login_issue` | Internet / Mobile Banking Login Problem Policy |
| `fraud_report` | Fraud and Unauthorised Transaction Reporting Policy |
| `otp_issue` | OTP Not Received / Expired OTP Policy |
| `kyc_update` | KYC Document Update Policy |
| `refund_request` | Refund Processing Policy |
| `general_inquiry` | General Customer Inquiry |

---

## Video Demo

🎬 **[Link to video demonstration](#)** *(update this link before submission)*

---

## License

For educational use only – VNUHCM University of Science, 2026.
