# QUICK START GUIDE - Risk Intelligence System

## What You Have

A fully-functional regulatory intelligence system with:
✅ 3 connectors (SEC, FINRA, Federal Register)
✅ AI-powered 4-step analysis pipeline
✅ Unified database schema
✅ 3 automated deliverables (Impact Digest, Task Backlog, Changelog)
✅ Interactive Streamlit dashboard

## First-Time Setup (5 minutes)

### Step 1: Install Python Packages
cd \""c:\Users\tuesingh\Desktop\Firm\2026_RiskIntelligence\impact-analysis\"\"
pip install -r requirements.txt

### Step 2: Set Your API Key
setx ANTHROPIC_API_KEY \"\"sk-your-api-key-here\"\"
# Or set in PowerShell:
\=\"\"sk-your-api-key-here\"\"

### Step 3: Verify Installation
python -c \"\"import anthropic; print('✓ Anthropic installed')'\"\"
python -c \"\"import streamlit; print('✓ Streamlit installed')'\"\"

## Running the System

### Option A: Command Line Pipeline (Batch Mode)
python utils/orchestrator.py

Output:
  - Ingests from SEC, FINRA, Federal Register
  - Analyzes unanalyzed items
  - Generates reports/impact_report_*.json
  - Generates reports/impact_analysis_*.csv

### Option B: Interactive Dashboard
streamlit run streamlit_app.py

Then:
1. Open http://localhost:8501 in browser
2. Click ▶️ Run Full Pipeline button in sidebar
3. View results in tabs (Impact Digest, Task Backlog, etc.)

## Expected Results

After first run, you should see:

**Database (regulatory_items.db):**
  - SEC press releases + litigation
  - FINRA notices
  - Federal Register documents
  - Total items by source

**Analysis Results:**
  - Relevance classification (Is it relevant to wealth management?)
  - Impact scores (5 dimensions: severity, time, ops, customer, enforcement)
  - Executive summaries (5 bullets per item)
  - Actionable tasks (with owner, due date, evidence needed)

**Reports (./reports/):**
  - impact_report_YYYYMMDD_HHMMSS.json - Full structured data
  - impact_analysis_YYYYMMDD_HHMMSS.csv - Excel-friendly export

## Dashboard Tour

**Sidebar:**
- ▶️ Pipeline Control - Run analysis
- 🚨 Active Alerts - Top high/critical items
- Quick Actions - View all items or export

**Main Tabs:**
1. **📊 Impact Digest** - Top 10 regulatory items ranked by impact
2. **📋 Task Backlog** - Prioritized tasks by owner (Compliance, Legal, Ops, etc.)
3. **📈 Analysis Details** - Filter all items by source/impact/area + deep dives
4. **🔄 Changelog** - What's new & escalated in last 24h

## Project Files

📁 utils/
  ├── orchestrator.py ........... Main pipeline (ingest → analyze → output)
  ├── connectors.py ............ SEC, FINRA, FedReg RSS/API fetchers
  ├── data_store.py ............ SQLite schema + queries
  ├── ai_analysis.py ........... 4-step Claude AI analysis
  └── output_generators.py ...... Report generators

📄 streamlit_app.py ............ Dashboard UI
📄 requirements.txt ............ Python dependencies
📄 README_SYSTEM.md ............ Full documentation

## Customization Tips

### Add Custom Keywords
Edit utils/connectors.py:
  FedRegConnector.KEYWORDS = ['your', 'keywords', 'here']

### Change AI Model
Edit utils/ai_analysis.py:
  self.model = 'claude-3-opus-20240229'  # Switch to different Claude model

### Schedule Daily Runs
Windows Task Scheduler:
  Program: C:\path\to\python.exe
  Arguments: utils/orchestrator.py
  Schedule: Daily at 8 AM

## Troubleshooting

### \"No module named 'anthropic'\"
→ pip install anthropic

### \"ANTHROPIC_API_KEY not found\"
→ setx ANTHROPIC_API_KEY \"\"your-key\"\"
→ Restart terminal/app

### \"Database is locked\"
→ Close any other database connections
→ rm regulatory_items.db (to reset)

### API Rate Limits
→ Add delays in connectors.py if needed:
  time.sleep(1)  # 1 second between requests

## What's Next?

### Phase 2 - Enhancements
- [ ] Email alerts for high-impact items
- [ ] Slack integration
- [ ] Historical impact tracking
- [ ] Compliance attestation workflow
- [ ] Vendor/client update distribution

### Phase 3 - Advanced Features
- [ ] Natural language search
- [ ] Sentiment analysis
- [ ] Predicted impact scoring
- [ ] Cross-item dependency detection
- [ ] Audit trail & version history

## Support

Questions or issues?
- Check README_SYSTEM.md for full documentation
- Review log messages for error details
- Verify all dependencies installed: pip list

---

**System Ready!** 🚀

Next Step: Click the \"▶️ Run Full Pipeline\" button in the Streamlit dashboard.

