import streamlit as st
from utils import db
from utils import news_agent
from utils.summarization import summarize_with_claude

db.initialize_db()

st.title("Home: Compliance Dashboard Overview")

num_regs = len(db.get_all_regulations())
num_policies = len(db.get_all_policies())
all_tasks = db.get_all_tasks()
open_tasks = len([t for t in all_tasks if t['status'] != 'Complete'])

st.markdown("""
#### Key Features:
- Regulatory updates summarized with AI
- Track affected policies and review status
- Assign and monitor compliance tasks
- View analytics and trends
""")

st.write(f"**Registered regulations:** {num_regs}")
st.write(f"**Registered policies:** {num_policies}")
st.write(f"**Open tasks:** {open_tasks}")

st.header("Quick Navigation")
navigation_targets = [
    ("Go to Regulatory Feed", "2_Regulatory_Feed"),
    ("Go to Policy Tracker", "3_Policy_Tracker"),
    ("Go to Task Manager", "4_Task_Manager"),
    ("Go to Analytics", "5_Analytics"),
    ("Go to Admin Tools", "6_Admin_Tools")
]

for label, page in navigation_targets:
    if st.button(label):
        st.experimental_set_query_params(page=page)
        st.success(f"Navigating to {label}...")
        st.experimental_rerun()

st.info("Or use the sidebar navigation menu at any time.")

# --- NEWS SUMMARY AGENT ---
st.header("News Summary: Policies Affecting Wealth Management Firms")

if st.button("Pull Latest News"):
    with st.spinner("Fetching and summarizing relevant news..."):
        news_api_key = st.secrets.get("NEWSAPI_KEY", "")
        articles = news_agent.fetch_wealth_management_news(news_api_key)
        if not articles:
            st.warning("No news articles found or API unreachable.")
        for i, article in enumerate(articles):
            st.subheader(f"{article['title']} ({article.get('publishedAt','')[:10]})")
            st.write(f"Source: {article.get('url','')}")
            st.write(article.get('description', ''))
            # AI summary: policy implication for wealth management
            summary_prompt = (
                "Based on this news article, what policy considerations or compliance impacts "
                "are there for a wealth management firm? Summarize for compliance officers:"
                f"\n\n{article.get('description','') or article.get('content','')}"
            )
            summary = news_agent.summarize_article_with_claude(
                summary_prompt,
                st.secrets["ANTHROPIC_API_KEY"],
                summarize_with_claude
            )
            st.success(f"AI Summary: {summary}")
            st.markdown("---")
