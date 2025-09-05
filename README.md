# PRISM Portfolio Builder

An AI-assisted **automated portfolio generation tool** developed during a hackathon.  
It integrates with the **MTS PRISM API** to generate client profiles, parse financial constraints, and build risk-aware portfolios based on age, budget, and investment horizon.

---

## ✨ Features

- 🔗 **API Client**: Connects securely to the PRISM challenge server  
- 🧠 **Context Parser**: Extracts age, gender, budget, salary, and investment horizon from natural-language text  
- 📊 **Allocation Logic**: Assigns budget across ETFs, stocks, and bonds using heuristics (age & time horizon)  
- ⚡ **CLI Interface**: Run locally with `--dry-run` to preview portfolios before submitting  
- 🛡️ **Error Handling & Retries**: Robust HTTP requests with retry logic and timeouts  
- 🔑 **Secrets Management**: Uses `.env` file for API keys (not committed to GitHub)  

---

## 🛠 Tech Stack

- **Python 3.10+**
- **Requests** (HTTP client with retries & error handling)  
- **python-dotenv** (environment variable management)  
- **Dataclasses** & **Type Hints** (structured, maintainable code)  
- **Regex** (for parsing natural language context)  
- **Logging** (debugging and auditability)  

---

## 📂 Project Structure

finance-portfolio-prism/
├─ prism_client.py # Handles API requests & context parsing
├─ portfolio.py # Portfolio allocation logic
├─ main.py # CLI entrypoint
├─ requirements.txt # Dependencies
├─ README.md # Documentation
├─ .gitignore # Ignored files (venv, .env, pycache)
└─ .env # API keys (never commit this!)

yaml
Copy code

---

## 🚀 Getting Started

### 1. Clone the repo
```bash
git clone https://github.com/<your-username>/finance-portfolio-prism.git
cd finance-portfolio-prism
2. Create a virtual environment
bash
Copy code
python -m venv venv
source venv/bin/activate      # Windows: .\venv\Scripts\Activate.ps1
3. Install dependencies
bash
Copy code
pip install -r requirements.txt
4. Add environment variables
Create a file called .env in the project root:

ini
Copy code
TEAM_API_CODE=your_api_key_here
URL=mts-prism.com
PORT=8082
5. Run
bash
Copy code
python main.py --dry-run   # preview portfolio
python main.py             # submit to server
📊 Example Output
css
Copy code
Team information: { ... }
Context provided: { "message": "Joe Lee, 53 years old, budget of $5,856..." }

Parsed context:
ParsedContext(name='Joe Lee', age=53, gender='male',
              budget=5856, salary=None,
              start_date='2010-08-14', end_date='2011-06-21')

Proposed positions: [('AAPL', 1), ('MSFT', 1), ('VOO', 2), ('IEF', 3)]
Evaluation response: { "score": 87, "comment": "Well balanced portfolio!" }
🔮 Future Improvements
 Smarter allocation strategy using machine learning (e.g., risk models, Markowitz optimisation)

 Add unit tests (pytest) for allocation & parsing

 Deploy as a FastAPI microservice with REST endpoints

 Web dashboard (Next.js + Plotly) for portfolio visualisation

🏆 Hackathon Context
This project was built as part of a finance hackathon where the challenge was to:

Parse dynamic client profiles from the PRISM API

Build personalised investment portfolios

Submit allocations for scoring & evaluation

⚠️ Disclaimer
This code is for educational and hackathon purposes only.
It does not provide financial advice and should not be used for real trading.
