# Risk Intelligence System - Wealth Management Regulatory Monitor

A comprehensive automated system for monitoring, analyzing, and managing regulatory changes impacting wealth management firms (RIAs, Broker-Dealers, Trading, Retirement platforms).

## 🎯 Key Features

### A. Ingest (3 Connectors)
- **SEC RSS Connector**: Press releases and litigation (title, date, description, link, category)
- **FINRA Connector**: Regulatory notices and news (RSS + HTML crawl with change detection)
- **Federal Register API**: SEC, DOL, Treasury/FinCEN documents filtered by keywords (investment adviser, broker-dealer, best interest, custody, AML, retirement)

### B. AI Analysis (4-Step Deterministic Pipeline)
1. **Relevance Filter**: Determines if item is relevant to wealth management (Yes/No + business area)
2. **Impact Scoring**: 5 dimensions (1-5 scale) → Overall impact (Low/Med/High/Critical)
   - Regulatory severity, Time sensitivity, Operational effort, Customer impact, Enforcement risk
3. **Executive Summary**: 5 bullets max (What happened, Who's affected, What changes, Timing, Evidence needed)
4. **Task Generation**: Actionable worklist with owner roles, due windows, evidence artifacts

### C. Output (3 Deliverables)
1. **Impact Digest**: Top 10 items with impact rating + 2-3 line summary
2. **Task Backlog**: Deduped, prioritized tasks by owner (Compliance, Legal, Supervision, Ops, Tech, Training)
3. **Changelog**: What's new + escalated items since last run

## 📁 Project Structure

\\\
impact-analysis/
├── streamlit_app.py              # Main Streamlit dashboard
├── requirements.txt              # Python dependencies
├── utils/
│   ├── orchestrator.py          # Main pipeline orchestrator
│   ├── connectors.py            # SEC, FINRA, FedReg connectors
│   ├── data_store.py            # SQLite database & schema
│   ├── ai_analysis.py           # 4-step AI analysis pipeline
│   └── output_generators.py     # Report generators (digest, backlog, changelog)
└── reports/                      # Generated reports (JSON + CSV)
\\\

## 🚀 Quick Start

### 1. Install Dependencies
\\\ash
pip install -r requirements.txt
\\\

### 2. Set Environment Variables
\\\ash
export ANTHROPIC_API_KEY="your-api-key"  # For Claude AI analysis
\\\

### 3. Run the Pipeline (CLI)
\\\ash
python utils/orchestrator.py
\\\
This will:
- Ingest items from all 3 sources
- Analyze up to 50 unanalyzed items
- Generate all 3 deliverables
- Export to JSON + CSV

### 4. Launch Dashboard
\\\ash
streamlit run streamlit_app.py
\\`\nopen http://localhost:8501
\\\

## 📊 Dashboard Features

### Sidebar Controls
- **▶️ Run Full Pipeline**: Execute complete ingest → analyze → generate workflow
- **Active Alerts**: Show top 3 high/critical items
- **Quick Actions**: View all items or export reports

### Main Tabs
1. **📊 Impact Digest**: Top regulatory items with impact ratings
2. **📋 Task Backlog**: Prioritized tasks grouped by owner role
3. **📈 Analysis Details**: Filter/search all analyzed items with detailed scores
4. **🔄 Changelog**: New items and escalations from last 24h

## 🔍 Normalized Data Schema

All items stored in unified \egulatory_items\ table:

\\\
- source: SEC | FINRA | FedReg
- type: press_release | litigation | notice | proposed_rule | final_rule
- published_at: datetime
- title: string
- summary_raw: text
- full_text: text (optional)
- url: string (unique)
- tags: list (keywords extracted)
- entities: list (firms/products/regs detected)
- is_relevant: 1/0
- relevance_reason: text
- business_area: RIA | Broker-Dealer | Retirement | AML | Marketing | Trading | Supervision | Custody | Operations
- impact_overall: Low | Medium | High | Critical
- impact_severity: 1-5
- impact_time_sensitivity: 1-5
- impact_operational_effort: 1-5
- impact_customer: 1-5
- impact_enforcement_risk: 1-5
- executive_summary: text
- tasks: json array
\\\

## 📝 Business Areas & Keywords

The system monitors these regulatory changes:
- **RIA**: Investment adviser registrations, fiduciary duty, compliance rules
- **Broker-Dealer**: Best execution, fair pricing, supervision requirements
- **Retirement**: ERISA, retirement plan custody, participant disclosures
- **AML**: Know-your-customer, beneficial ownership, sanctions
- **Marketing**: Communication rules, advertising standards
- **Trading**: Market manipulation, insider trading, best execution
- **Supervision**: Firm compliance programs, surveillance, audit trails
- **Custody**: Asset safeguarding, valuation, segregation

## 🤖 AI Analysis Details

The system uses Claude AI to perform deterministic analysis with structured prompts:

**Step 1: Relevance Filter**
- Input: Item title + summary
- Output: relevant (bool) + business_area + reason
- Routes to Step 2 only if relevant

**Step 2: Impact Scoring**
- Evaluates 5 dimensions independently (1-5 scale)
- Calculates overall impact from average score
- Transparent rubric provided to AI model

**Step 3: Executive Summary**
- Generates exactly 5 bullets in specified format
- Focuses on: What, Who, Changes, Timing, Evidence
- Designed for compliance team consumption

**Step 4: Task Generation**
- Creates 3-5 actionable tasks per item
- Assigns owner_role, due_window, evidence_artifact
- Tracks dependencies between tasks

## 📊 Report Exports

### JSON Report
\impact_report_YYYYMMDD_HHMMSS.json\
Contains all 3 deliverables with full metadata:
- impact_digest: top items with scores
- task_backlog: deduped, prioritized tasks
- changelog: new + escalated items

### CSV Report
\impact_analysis_YYYYMMDD_HHMMSS.csv\
Excel-friendly format with:
- ID, Title, Source, Type, Published, Impact, All scores, Business Area, Summary, URL

## ⚙️ Configuration

### Connector Settings
Edit \utils/connectors.py\:
- SEC_PRESS_RELEASE_FEED: RSS URL
- FINRA_RSS_FEED: FINRA news/notices feed
- FED_REG_AGENCIES: ['SEC', 'DOL', 'TREASURY']
- FED_REG_KEYWORDS: Keywords to monitor

### Analysis Settings
Edit \utils/ai_analysis.py\:
- model: Claude model version (default: claude-3-5-sonnet-20241022)
- max_tokens: Adjust for response length
- Modify prompts for custom analysis criteria

### Database
\utils/data_store.py\:
- db_url: Default is \sqlite:///./regulatory_items.db\
- Change to PostgreSQL: \postgresql://user:pass@host/db\

## 🔄 Scheduling

For continuous monitoring, use a task scheduler:

### Linux/Mac (cron)
\\\ash
# Run pipeline daily at 8 AM
0 8 * * * cd /path/to/impact-analysis && python utils/orchestrator.py
\\\

### Windows (Task Scheduler)
\\\
Program: python
Arguments: utils/orchestrator.py
Working Directory: C:\path\to\impact-analysis
Triggers: Daily at 8:00 AM
\\\

### Docker (Recommended)
\\\dockerfile
FROM python:3.11
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "utils/orchestrator.py"]
\\\

## 📧 Notifications (Future Enhancement)

Integrate with:
- **Email**: Send digest + tasks to stakeholders
- **Slack**: Post high-impact items to #compliance
- **Teams**: Alert legal team of critical items
- **Jira**: Auto-create tickets from tasks

## 🔐 Security Considerations

- Store ANTHROPIC_API_KEY in environment, never hardcode
- Restrict database access to compliance team
- Use HTTPS for Federal Register API calls
- Implement rate limiting for RSS feeds
- Audit all report exports

## 📚 References

- [SEC RSS Feeds](https://www.sec.gov/rss)
- [FINRA Regulatory Notices](https://www.finra.org/rules-guidance/key-topics/regulatory-notices)
- [Federal Register API](https://www.federalregister.gov/api/v1)
- [Anthropic Claude API](https://docs.anthropic.com/)

## 🤝 Support & Contribution

For issues, feature requests, or improvements, contact the Compliance Tech team.

---

**Version**: 1.0  
**Last Updated**: January 21, 2026  
**Maintained By**: Risk Intelligence Team
