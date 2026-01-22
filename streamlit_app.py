import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
import json
import os
from pathlib import Path
from utils.orchestrator import RegulatoryIntelligenceOrchestrator
from utils.data_store import DataStore, RegulatoryItem
from sqlalchemy import desc

# Page configuration
st.set_page_config(
    page_title="Edward Jones - Risk Intelligence Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
    <style>
    /* Main header styling */
    .main-header {
        background-color: #002855;
        padding: 1rem 2rem;
        color: white;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin: -1rem -1rem 2rem -1rem;
    }
    
    .logo-section {
        font-size: 1.5rem;
        font-weight: bold;
        color: white;
    }
    
    .nav-menu {
        display: flex;
        gap: 2rem;
    }
    
    .nav-item {
        color: white;
        text-decoration: none;
        padding: 0.5rem 1rem;
        border-radius: 4px;
        transition: background-color 0.3s;
    }
    
    .nav-item:hover {
        background-color: rgba(255, 255, 255, 0.1);
    }
    
    .user-section {
        display: flex;
        gap: 1rem;
        align-items: center;
    }
    
    /* Alert cards */
    .alert-card {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 1rem;
        margin-bottom: 1rem;
        border-radius: 4px;
    }
    
    .alert-card-high {
        background-color: #f8d7da;
        border-left: 4px solid #dc3545;
    }
    
    .alert-card-info {
        background-color: #d1ecf1;
        border-left: 4px solid #17a2b8;
    }
    
    /* Deadline cards */
    .deadline-card {
        background-color: white;
        border: 1px solid #dee2e6;
        padding: 1rem;
        margin-bottom: 0.5rem;
        border-radius: 4px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    
    .deadline-urgent {
        border-left: 4px solid #dc3545;
    }
    
    .deadline-soon {
        border-left: 4px solid #ffc107;
    }
    
    .deadline-normal {
        border-left: 4px solid #28a745;
    }
    
    /* Status badges */
    .badge {
        display: inline-block;
        padding: 0.25rem 0.5rem;
        border-radius: 4px;
        font-size: 0.875rem;
        font-weight: 600;
    }
    
    .badge-danger {
        background-color: #dc3545;
        color: white;
    }
    
    .badge-warning {
        background-color: #ffc107;
        color: #212529;
    }
    
    .badge-info {
        background-color: #17a2b8;
        color: white;
    }
    
    .badge-success {
        background-color: #28a745;
        color: white;
    }
    
    /* Section headers */
    .section-header {
        font-size: 1.2rem;
        font-weight: 600;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #002855;
    }
    
    /* Timeline styling */
    .timeline-item {
        display: flex;
        gap: 1rem;
        margin-bottom: 1rem;
        padding-bottom: 1rem;
        border-bottom: 1px solid #dee2e6;
    }
    
    .timeline-date {
        min-width: 80px;
        font-weight: 600;
        color: #002855;
    }
    
    .timeline-content {
        flex: 1;
    }
    
    /* Chatbot styling */
    .chat-container {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 8px;
        padding: 1rem;
        min-height: 300px;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state and database
@st.cache_resource
def get_orchestrator():
    return RegulatoryIntelligenceOrchestrator()

@st.cache_resource
def get_data_store():
    return DataStore()

orchestrator = get_orchestrator()
data_store = get_data_store()

# Top Navigation Header
st.markdown("""
    <div class="main-header">
        <div class="logo-section">
            🏛️ Edward Jones | Risk Intelligence
        </div>
        <div class="nav-menu">
            <a href="#" class="nav-item">📊 Dashboard</a>
            <a href="#" class="nav-item">📋 Regulations</a>
            <a href="#" class="nav-item">📄 Filings</a>
            <a href="#" class="nav-item">📊 Reports</a>
            <a href="#" class="nav-item">⚙️ Settings</a>
        </div>
        <div class="user-section">
            <input type="text" placeholder="🔍 Search..." style="padding: 0.5rem; border-radius: 4px; border: none;">
            <span style="font-size: 1.2rem; cursor: pointer;">🔔</span>
            <span style="font-size: 1rem;">👤 Tue Singh</span>
        </div>
    </div>
""", unsafe_allow_html=True)

# Sidebar - Active Alerts
with st.sidebar:
    st.markdown('<div class="section-header">⚙️ Pipeline Control</div>', unsafe_allow_html=True)
    
    # Run full pipeline button
    if st.button("▶️ Run Full Pipeline", use_container_width=True, help="Ingest, analyze, and generate deliverables"):
        with st.spinner("Running pipeline... This may take a few minutes"):
            try:
                results = orchestrator.run_full_pipeline(limit_analysis=50)
                st.success(f"""
                ✅ Pipeline Complete!
                - **Ingested**: {results['ingested']} items
                - **Analyzed**: {results['analyzed']} items  
                - **Reports**: JSON + CSV generated
                """)
            except Exception as e:
                st.error(f"Pipeline error: {str(e)}")
    
    st.markdown("---")
    st.markdown('<div class="section-header">🚨 Active Alerts</div>', unsafe_allow_html=True)
    
    # Get high-impact items
    high_impact = data_store.get_high_impact_items()
    
    if high_impact:
        st.markdown(f"**{len(high_impact)} High/Critical items detected**")
        for item in high_impact[:3]:
            st.markdown(f"""
                <div class="alert-card alert-card-high">
                    <div style="font-weight: 600; margin-bottom: 0.5rem;">
                        <span class="badge badge-danger">{item.impact_overall}</span>
                    </div>
                    <div style="font-size: 0.875rem;">{item.title[:60]}...</div>
                    <div style="font-size: 0.75rem; color: #6c757d; margin-top: 0.5rem;">
                        {item.source} • {item.published_at.strftime('%m/%d/%Y') if item.published_at else 'N/A'}
                    </div>
                </div>
            """, unsafe_allow_html=True)
        
        if len(high_impact) > 3:
            st.markdown(f"_+{len(high_impact)-3} more high-impact items_")
    else:
        st.markdown("""
            <div class="alert-card alert-card-info">
                <div style="font-weight: 600; margin-bottom: 0.5rem;">
                    <span class="badge badge-success">✓</span> No Critical Items
                </div>
                <div style="font-size: 0.875rem;">
                    All analyzed items are Low or Medium impact.
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("**Quick Actions**")
    if st.button("📊 View All Items", use_container_width=True):
        st.session_state.view_all = True
    if st.button("📋 Export Reports", use_container_width=True):
        st.session_state.export = True

# Main Content Area
col1, col2 = st.columns([1, 2])

# Left Column - Upcoming Deadlines & High Risk Items
with col1:
    st.markdown('<div class="section-header">📅 Upcoming Deadlines</div>', unsafe_allow_html=True)
    
    # Form 13F Filing
    st.markdown("""
        <div class="deadline-card deadline-urgent">
            <div style="display: flex; justify-content: space-between; align-items: start;">
                <div>
                    <div style="font-weight: 600;">Form 13F Filing</div>
                    <div style="font-size: 0.875rem; color: #6c757d;">Q4 2024 Holdings Report</div>
                </div>
                <span class="badge badge-danger">2 Days</span>
            </div>
            <div style="margin-top: 0.5rem; font-size: 0.875rem;">
                Due: February 14, 2025
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Form ADV Update
    st.markdown("""
        <div class="deadline-card deadline-soon">
            <div style="display: flex; justify-content: space-between; align-items: start;">
                <div>
                    <div style="font-weight: 600;">Form ADV Update</div>
                    <div style="font-size: 0.875rem; color: #6c757d;">Annual Amendment</div>
                </div>
                <span class="badge badge-warning">7 Days</span>
            </div>
            <div style="margin-top: 0.5rem; font-size: 0.875rem;">
                Due: February 19, 2025
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Quarterly Review
    st.markdown("""
        <div class="deadline-card deadline-normal">
            <div style="display: flex; justify-content: space-between; align-items: start;">
                <div>
                    <div style="font-weight: 600;">Quarterly Review</div>
                    <div style="font-size: 0.875rem; color: #6c757d;">Compliance Assessment</div>
                </div>
                <span class="badge badge-success">14 Days</span>
            </div>
            <div style="margin-top: 0.5rem; font-size: 0.875rem;">
                Due: February 26, 2025
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # High Risk Items
    st.markdown('<div class="section-header">⚠️ High Risk Items</div>', unsafe_allow_html=True)
    
    risk_data = pd.DataFrame({
        'Source': ['SEC', 'FINRA', 'CFTC', 'State Regulators'],
        'Open Items': [3, 1, 2, 1],
        'Priority': ['High', 'Medium', 'High', 'Low']
    })
    
    for idx, row in risk_data.iterrows():
        priority_color = {
            'High': 'badge-danger',
            'Medium': 'badge-warning',
            'Low': 'badge-success'
        }[row['Priority']]
        
        st.markdown(f"""
            <div class="deadline-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <strong>{row['Source']}</strong>
                        <div style="font-size: 0.875rem; color: #6c757d;">{row['Open Items']} open items</div>
                    </div>
                    <span class="badge {priority_color}">{row['Priority']}</span>
                </div>
            </div>
        """, unsafe_allow_html=True)

# Right Column - Main Dashboard Content
with col2:
    # Active Alerts Section
    st.markdown('<div class="section-header">🔔 Active Alerts</div>', unsafe_allow_html=True)
    
    alert_col1, alert_col2 = st.columns(2)
    
    with alert_col1:
        st.metric("Pending Filings", "5", delta="+2 this week", delta_color="inverse")
    
    with alert_col2:
        st.metric("Active Alerts", "12", delta="+3 today", delta_color="inverse")
    
    st.markdown("---")
    
    # Priority Alerts Section
    st.markdown('<div class="section-header">⚡ Priority Alerts</div>', unsafe_allow_html=True)
    
    priority_alerts = [
        {"title": "SEC Form CRS Update Required", "category": "Filing", "urgency": "High", "date": "2 days ago"},
        {"title": "FINRA Rule 2111 Compliance Check", "category": "Compliance", "urgency": "Medium", "date": "1 week ago"},
        {"title": "New AML Policy Review", "category": "Policy", "urgency": "High", "date": "3 days ago"}
    ]
    
    for alert in priority_alerts:
        urgency_badge = "badge-danger" if alert['urgency'] == "High" else "badge-warning"
        st.markdown(f"""
            <div class="deadline-card">
                <div style="display: flex; justify-content: space-between;">
                    <div style="flex: 1;">
                        <div style="font-weight: 600;">{alert['title']}</div>
                        <div style="font-size: 0.875rem; color: #6c757d; margin-top: 0.25rem;">
                            {alert['category']} • {alert['date']}
                        </div>
                    </div>
                    <span class="badge {urgency_badge}">{alert['urgency']}</span>
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Compliance Timeline
    st.markdown('<div class="section-header">📆 Upcoming Compliance Activities</div>', unsafe_allow_html=True)
    
    timeline_items = [
        {"date": "Feb 14", "activity": "Form 13F Filing Deadline", "status": "Urgent"},
        {"date": "Feb 19", "activity": "Form ADV Annual Amendment", "status": "Pending"},
        {"date": "Feb 26", "activity": "Q1 Compliance Review Meeting", "status": "Scheduled"},
        {"date": "Mar 5", "activity": "FINRA Audit Preparation", "status": "Scheduled"},
        {"date": "Mar 15", "activity": "State Registration Renewals", "status": "Scheduled"}
    ]
    
    for item in timeline_items:
        status_badge = {
            'Urgent': 'badge-danger',
            'Pending': 'badge-warning',
            'Scheduled': 'badge-info'
        }[item['status']]
        
        st.markdown(f"""
            <div class="timeline-item">
                <div class="timeline-date">{item['date']}</div>
                <div class="timeline-content">
                    <div style="font-weight: 600;">{item['activity']}</div>
                    <span class="badge {status_badge}">{item['status']}</span>
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Chatbot Section
    st.markdown('<div class="section-header">💬 Compliance Assistant</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    
    # Chat interface
    user_input = st.text_input("Ask about regulations, deadlines, or compliance requirements...", 
                                placeholder="e.g., 'What are the Form ADV filing requirements?'",
                                label_visibility="collapsed")
    
    if user_input:
        st.markdown(f"""
            <div style="background-color: #e3f2fd; padding: 0.75rem; border-radius: 8px; margin: 0.5rem 0;">
                <strong>You:</strong> {user_input}
            </div>
        """, unsafe_allow_html=True)
        
        # Simulated response
        st.markdown("""
            <div style="background-color: white; padding: 0.75rem; border-radius: 8px; margin: 0.5rem 0; border: 1px solid #dee2e6;">
                <strong>Assistant:</strong> I can help you with that. Form ADV must be filed annually within 90 days of fiscal year end...
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <div style="text-align: center; color: #6c757d; padding: 2rem;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">💬</div>
                <div>Ask me anything about compliance, regulations, or upcoming deadlines</div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Bottom Section - Analysis Results & Tabs
st.markdown("---")

# Create tabs for different views
tab1, tab2, tab3, tab4 = st.tabs(["📊 Impact Digest", "📋 Task Backlog", "📈 Analysis Details", "🔄 Changelog"])

with tab1:
    st.markdown("<h3>Impact Digest - Top Regulatory Items</h3>", unsafe_allow_html=True)
    
    # Get all items and generate digest
    all_items = data_store.session.query(RegulatoryItem).filter(
        RegulatoryItem.is_relevant == 1
    ).order_by(desc(RegulatoryItem.impact_overall)).limit(10).all()
    
    if all_items:
        digest_data = []
        for item in all_items:
            digest_data.append({
                'Title': item.title[:70],
                'Source': item.source,
                'Type': item.type,
                'Impact': item.impact_overall or 'N/A',
                'Business Area': item.business_area or 'N/A',
                'Published': item.published_at.strftime('%m/%d') if item.published_at else 'N/A',
            })
        
        st.dataframe(pd.DataFrame(digest_data), use_container_width=True)
        
        # Show expanded view of top item
        if all_items:
            st.markdown("<h4>Top Priority Item</h4>", unsafe_allow_html=True)
            top_item = all_items[0]
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Impact Level", top_item.impact_overall or "N/A")
            with col2:
                st.metric("Business Area", top_item.business_area or "N/A")
            with col3:
                st.metric("Source", top_item.source)
            
            st.markdown(f"**{top_item.title}**")
            st.markdown(f"📅 Published: {top_item.published_at.strftime('%B %d, %Y') if top_item.published_at else 'N/A'}")
            st.markdown(f"🔗 [View Source]({top_item.url})")
            
            if top_item.executive_summary:
                st.markdown("<strong>Executive Summary:</strong>", unsafe_allow_html=True)
                st.markdown(top_item.executive_summary)
    else:
        st.info("No analyzed items yet. Run the pipeline to analyze regulatory items.")

with tab2:
    st.markdown("<h3>Task Backlog - Actionable Items</h3>", unsafe_allow_html=True)
    
    # Get all items with tasks
    all_items = data_store.session.query(RegulatoryItem).filter(
        RegulatoryItem.tasks != None
    ).all()
    
    if all_items:
        task_list = []
        for item in all_items:
            try:
                tasks = json.loads(item.tasks) if isinstance(item.tasks, str) else item.tasks or []
                for task in tasks:
                    task_list.append({
                        'Task': task.get('task', 'N/A')[:70],
                        'Owner': task.get('owner_role', 'N/A'),
                        'Due': task.get('due_window', 'N/A'),
                        'Evidence': task.get('evidence_artifact', 'N/A')[:40],
                        'Impact Item': item.title[:50],
                    })
            except:
                pass
        
        if task_list:
            task_df = pd.DataFrame(task_list)
            st.dataframe(task_df, use_container_width=True)
            
            # Group by owner
            st.markdown("<h4>Tasks by Owner</h4>", unsafe_allow_html=True)
            for owner in task_df['Owner'].unique():
                owner_tasks = task_df[task_df['Owner'] == owner]
                st.markdown(f"**{owner}** ({len(owner_tasks)} tasks)")
                for _, row in owner_tasks.iterrows():
                    st.markdown(f"  - {row['Task']} (Due: {row['Due']})")
        else:
            st.info("No tasks generated yet.")
    else:
        st.info("No items with tasks yet.")

with tab3:
    st.markdown("<h3>Detailed Analysis</h3>", unsafe_allow_html=True)
    
    # Show all analyzed items with detail
    all_items = data_store.session.query(RegulatoryItem).filter(
        RegulatoryItem.is_relevant == 1
    ).order_by(desc(RegulatoryItem.published_at)).all()
    
    if all_items:
        # Filter options
        col1, col2, col3 = st.columns(3)
        with col1:
            source_filter = st.multiselect("Source", ['SEC', 'FINRA', 'FedReg'], default=['SEC', 'FINRA', 'FedReg'])
        with col2:
            impact_filter = st.multiselect("Impact", ['Critical', 'High', 'Medium', 'Low'], default=['Critical', 'High'])
        with col3:
            area_filter = st.multiselect("Business Area", 
                                        ['RIA', 'Broker-Dealer', 'Retirement', 'AML', 'Marketing', 'Trading', 'Supervision', 'Custody'],
                                        default=['RIA', 'Broker-Dealer', 'Retirement'])
        
        filtered_items = [i for i in all_items if i.source in source_filter and i.impact_overall in impact_filter and i.business_area in area_filter]
        
        st.markdown(f"**Showing {len(filtered_items)} of {len(all_items)} items**")
        
        for item in filtered_items[:20]:  # Show max 20
            with st.expander(f"{item.title[:60]} ({item.impact_overall}) - {item.source}"):
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.markdown(f"**Type:** {item.type}")
                with col2:
                    st.markdown(f"**Area:** {item.business_area or 'N/A'}")
                with col3:
                    st.markdown(f"**Published:** {item.published_at.strftime('%m/%d') if item.published_at else 'N/A'}")
                with col4:
                    st.markdown(f"**Impact:** {item.impact_overall or 'N/A'}")
                
                st.markdown("**Impact Scores:**")
                score_col1, score_col2, score_col3, score_col4, score_col5 = st.columns(5)
                with score_col1:
                    st.metric("Severity", item.impact_severity or "-")
                with score_col2:
                    st.metric("Time Sens", item.impact_time_sensitivity or "-")
                with score_col3:
                    st.metric("Ops Effort", item.impact_operational_effort or "-")
                with score_col4:
                    st.metric("Customer", item.impact_customer or "-")
                with score_col5:
                    st.metric("Enforce Risk", item.impact_enforcement_risk or "-")
                
                if item.executive_summary:
                    st.markdown("**Summary:**")
                    st.markdown(item.executive_summary)
                
                st.markdown(f"[📌 View Full Source]({item.url})")
    else:
        st.info("No analyzed items yet.")

with tab4:
    st.markdown("<h3>Recent Changes & Escalations</h3>", unsafe_allow_html=True)
    
    # Get items from last 24 hours
    last_24h = datetime.utcnow() - timedelta(hours=24)
    new_items = data_store.session.query(RegulatoryItem).filter(
        RegulatoryItem.ingested_at > last_24h
    ).order_by(desc(RegulatoryItem.published_at)).all()
    
    escalated_items = [i for i in new_items if i.impact_overall in ['High', 'Critical']]
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("New Items (24h)", len(new_items))
    with col2:
        st.metric("Escalated", len(escalated_items))
    with col3:
        st.metric("Total in DB", data_store.session.query(RegulatoryItem).count())
    
    st.markdown("---")
    
    if new_items:
        st.markdown(f"<h4>New Items ({len(new_items)})</h4>", unsafe_allow_html=True)
        for item in new_items[:10]:
            st.markdown(f"""
            - **{item.title}**  
              {item.source} | {item.type} | {item.published_at.strftime('%m/%d %H:%M') if item.published_at else 'N/A'}
            """)
    
    if escalated_items:
        st.markdown(f"<h4>⚠️ Escalated Items ({len(escalated_items)})</h4>", unsafe_allow_html=True)
        for item in escalated_items:
            st.markdown(f"""
            - **{item.title}**  
              {item.source} | Impact: **{item.impact_overall}** | {item.business_area or 'General'}
            """)

# Footer
st.markdown("---")
footer_time = datetime.now().strftime('%B %d, %Y %I:%M %p')
st.markdown(f"""
    <div style="text-align: center; color: #6c757d; font-size: 0.875rem; padding: 1rem;">
        Edward Jones Risk Intelligence Dashboard | Last Updated: {footer_time}
    </div>
""", unsafe_allow_html=True)
