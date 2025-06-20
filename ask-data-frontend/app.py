"""
AskData Analytics - Simple Streamlit Frontend
Professional 3-tab interface with dark/light theme support.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import time

# Import our simple modules
import config
from api_client import api
from database import db

# Page config
st.set_page_config(
    page_title=config.APP_TITLE,
    page_icon=config.APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if "theme" not in st.session_state:
    st.session_state.theme = "light"
if "current_tab" not in st.session_state:
    st.session_state.current_tab = "Query"
if "last_query_id" not in st.session_state:
    st.session_state.last_query_id = None

def apply_theme():
    """Apply professional theme styling."""
    theme = st.session_state.theme
    
    if theme == "dark":
        primary_color = "#4da6ff"
        bg_color = "#0e1117"
        secondary_bg = "#262730"
        text_color = "#fafafa"
        border_color = "#404040"
    else:
        primary_color = "#0066cc"
        bg_color = "#ffffff"
        secondary_bg = "#f0f2f6"
        text_color = "#262730"
        border_color = "#e1e5e9"
    
    css = f"""
    <style>
    .main .block-container {{
        padding-top: 2rem;
        padding-bottom: 2rem;
    }}
    
    .metric-card {{
        background-color: {secondary_bg};
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid {border_color};
        margin: 0.5rem 0;
    }}
    
    .status-online {{ color: #28a745; }}
    .status-offline {{ color: #dc3545; }}
    
    .stButton > button {{
        border-radius: 4px;
        border: 1px solid {border_color};
        background-color: {secondary_bg};
        color: {text_color};
    }}
    
    .stButton > button:hover {{
        border-color: {primary_color};
        color: {primary_color};
    }}
    
    .sql-code {{
        background-color: {secondary_bg};
        border: 1px solid {border_color};
        border-radius: 4px;
        padding: 1rem;
        font-family: 'Courier New', monospace;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

def render_header():
    """Render app header with theme toggle."""
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col1:
        st.title(f"{config.APP_ICON} {config.APP_TITLE}")
    
    with col2:
        # Backend status
        success, _ = api.health_check()
        status = "🟢 Online" if success else "🔴 Offline"
        st.write(f"**Status:** {status}")
    
    with col3:
        # Theme toggle
        theme_icon = "🌙" if st.session_state.theme == "light" else "☀️"
        if st.button(theme_icon, help="Toggle theme"):
            st.session_state.theme = "dark" if st.session_state.theme == "light" else "light"
            st.rerun()

def render_sidebar():
    """Render professional sidebar navigation."""
    st.sidebar.title("Navigation")
    
    # Navigation buttons
    tabs = ["Query", "Dashboard", "Admin"]
    
    for tab in tabs:
        # Icon mapping
        icons = {"Query": "🔍", "Dashboard": "📊", "Admin": "⚙️"}
        
        if st.sidebar.button(f"{icons[tab]} {tab}", key=f"nav_{tab}", use_container_width=True):
            st.session_state.current_tab = tab
            st.rerun()
    
    st.sidebar.divider()
    
    # Recent queries
    st.sidebar.subheader("Recent Queries")
    recent = db.get_recent_queries(5)
    
    if recent:
        for query in recent[:3]:  # Show top 3
            question = query['question'][:30] + "..." if len(query['question']) > 30 else query['question']
            success_icon = "✅" if query['success'] else "❌"
            st.sidebar.text(f"{success_icon} {question}")
    else:
        st.sidebar.text("No queries yet")
    
    st.sidebar.divider()
    
    # Quick stats
    stats = db.get_stats()
    st.sidebar.metric("Total Queries", stats['total_queries'])
    st.sidebar.metric("Success Rate", f"{stats['success_rate']}%")

def render_query_tab():
    """Tab 1: Query Interface."""
    st.header("🔍 Ask Your Question")
    
    # Query input
    col1, col2 = st.columns([3, 1])
    
    with col1:
        question = st.text_area(
            "Enter your question in natural language:",
            placeholder="e.g., Show me recent records with high values",
            height=100
        )
    
    with col2:
        st.write("**Settings**")
        max_tables = st.selectbox("Max Tables", [2, 3, 4, 5], index=2)
        execute_sql = st.checkbox("Execute SQL", value=True)
    
    # Generate button
    if st.button("Generate SQL", type="primary", use_container_width=True):
        if not question.strip():
            st.error("Please enter a question!")
            return
        
        with st.spinner("Generating SQL..."):
            start_time = time.time()
            success, response = api.generate_sql(question, max_tables, execute_sql)
            execution_time = int((time.time() - start_time) * 1000)
        
        if success:
            # Log successful query
            query_id = db.log_query(
                question=question,
                sql_query=response.get('sql_query', ''),
                success=response.get('success', False),
                executed=response.get('executed', False),
                row_count=response.get('row_count', 0),
                execution_time_ms=execution_time,
                error_message=response.get('error_message', '')
            )
            st.session_state.last_query_id = query_id
            
            # Display results
            st.success("✅ SQL generated successfully!")
            
            # SQL Query
            st.subheader("Generated SQL")
            sql_query = response.get('sql_query', '')
            st.code(sql_query, language='sql')
            
            # Selected tables
            if 'selected_tables' in response:
                st.write(f"**Selected Tables:** {', '.join(response['selected_tables'])}")
            
            # Execution results
            if response.get('executed') and response.get('data'):
                st.subheader("Query Results")
                df = pd.DataFrame(response['data'])
                st.dataframe(df, use_container_width=True)
                st.write(f"**Rows returned:** {response.get('row_count', 0)}")
            
            # Execution info
            st.write(f"**Execution time:** {execution_time}ms")
            
        else:
            # Log failed query
            db.log_query(
                question=question,
                success=False,
                error_message=response.get('message', 'Unknown error'),
                execution_time_ms=execution_time
            )
            
            st.error(f"❌ Error: {response.get('message', 'Unknown error')}")
    
    # Feedback section
    if st.session_state.last_query_id:
        st.divider()
        st.subheader("Feedback")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("👍 Good Result", use_container_width=True):
                db.add_feedback(st.session_state.last_query_id, 1)
                st.success("Thanks for your feedback!")
        
        with col2:
            if st.button("👎 Bad Result", use_container_width=True):
                db.add_feedback(st.session_state.last_query_id, -1)
                st.success("Thanks for your feedback!")

def render_dashboard_tab():
    """Tab 2: Analytics Dashboard."""
    st.header("📊 Analytics Dashboard")
    
    # Get statistics
    stats = db.get_stats()
    recent_queries = db.get_recent_queries(50)
    
    # Enhanced statistics - get feedback counts
    cursor = db.conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM query_logs WHERE feedback = 1")
    good_feedback = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM query_logs WHERE feedback = -1")
    bad_feedback = cursor.fetchone()[0]
    
    # KPI Cards
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Total Queries", stats['total_queries'])
    
    with col2:
        st.metric("Success Rate", f"{stats['success_rate']}%")
    
    with col3:
        st.metric("Avg Response Time", f"{stats['avg_execution_time']}ms")
    
    with col4:
        st.metric("👍 Good Feedback", good_feedback)
    
    with col5:
        st.metric("👎 Bad Feedback", bad_feedback)
    
    st.divider()
    
    # Charts and data
    if recent_queries:
        # Success rate over time - fixed chart
        st.subheader("Query Success Over Time")
        df = pd.DataFrame(recent_queries)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['success_int'] = df['success'].astype(int)
        
        # Create a simple time series with all data points
        fig = px.scatter(
            df, 
            x='timestamp', 
            y='success_int', 
            title='Query Success Over Time',
            labels={'success_int': 'Success (1=Success, 0=Failure)', 'timestamp': 'Time'},
            hover_data=['question']
        )
        
        # Add trend line if we have enough data
        if len(df) > 3:
            # Add moving average
            df_sorted = df.sort_values('timestamp')
            df_sorted['moving_avg'] = df_sorted['success_int'].rolling(window=3, min_periods=1).mean()
            
            fig.add_trace(
                go.Scatter(
                    x=df_sorted['timestamp'],
                    y=df_sorted['moving_avg'],
                    mode='lines',
                    name='Moving Average',
                    line=dict(color='red', width=2)
                )
            )
        
        fig.update_layout(
            yaxis=dict(
                title="Success Rate",
                range=[-0.1, 1.1],
                tickvals=[0, 1],
                ticktext=['Failure', 'Success']
            ),
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Query log table with search functionality
        st.subheader("Recent Query Log")
        
        # Add search box
        search_query = st.text_input(
            "🔍 Search queries:",
            placeholder="Enter keywords to filter queries...",
            help="Search in questions, status, or feedback"
        )
        
        # Prepare data for display
        display_df = df[['timestamp', 'question', 'success', 'executed', 'row_count', 'feedback']].copy()
        display_df['timestamp'] = display_df['timestamp'].dt.strftime('%Y-%m-%d %H:%M')
        
        # Add feedback column with icons
        def format_feedback(feedback_val):
            if feedback_val == 1:
                return "👍 Good"
            elif feedback_val == -1:
                return "👎 Bad"
            else:
                return "🤷 No feedback"
        
        display_df['feedback_text'] = display_df['feedback'].apply(format_feedback)
        display_df['success_text'] = display_df['success'].apply(lambda x: "✅ Success" if x else "❌ Failed")
        
        # Apply search filter if provided
        if search_query:
            search_lower = search_query.lower()
            mask = (
                display_df['question'].str.lower().str.contains(search_lower, na=False) |
                display_df['success_text'].str.lower().str.contains(search_lower, na=False) |
                display_df['feedback_text'].str.lower().str.contains(search_lower, na=False)
            )
            display_df = display_df[mask]
            
            # Show search results count
            if len(display_df) == 0:
                st.warning(f"No queries found matching '{search_query}'")
            else:
                st.info(f"Found {len(display_df)} queries matching '{search_query}'")
        
        # Reorder columns for better display
        display_df = display_df[['timestamp', 'question', 'success_text', 'executed', 'row_count', 'feedback_text']]
        display_df.columns = ['Time', 'Question', 'Status', 'Executed', 'Rows', 'Feedback']
        
        st.dataframe(display_df, use_container_width=True)
        
        # Summary stats
        st.subheader("Query Statistics")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            avg_length = df['question'].str.len().mean()
            st.metric("Avg Question Length", f"{avg_length:.0f} chars")
        
        with col2:
            executed_count = df['executed'].sum()
            st.metric("Queries Executed", f"{executed_count}/{len(df)}")
        
        with col3:
            total_rows = df['row_count'].sum()
            st.metric("Total Rows Returned", f"{total_rows:,}")
    
    else:
        st.info("No queries logged yet. Try the Query tab to get started!")

def render_admin_tab():
    """Tab 3: Admin Panel."""
    st.header("⚙️ Admin Panel")
    global db

    # Backend status
    st.subheader("Backend Status")
    success, response = api.health_check()
    
    if success:
        st.success("✅ Backend is online")
        
        # Show backend details
        if 'tables_available' in response:
            st.write(f"**Tables Available:** {response['tables_available']}")
        if 'database' in response:
            st.write(f"**Database Status:** {response['database']}")
    else:
        st.error("❌ Backend is offline")
        st.write(f"**Error:** {response.get('message', 'Unknown error')}")
    
    st.divider()
    
    # Schema information
    st.subheader("Database Schema")
    
    if st.button("🔄 Refresh Schema Info"):
        with st.spinner("Loading schema..."):
            success, schema_response = api.get_schema()
        
        if success:
            st.success("✅ Schema loaded successfully")
            
            # Show tables
            if 'tables' in schema_response:
                st.write(f"**Available Tables ({len(schema_response['tables'])}):**")
                
                # Display as columns
                tables = schema_response['tables']
                cols = st.columns(3)
                for i, table in enumerate(tables):
                    with cols[i % 3]:
                        st.write(f"• {table}")
            
            # Show schema summary
            if 'schema_summary' in schema_response:
                st.subheader("Schema Summary")
                st.text(schema_response['schema_summary'])
        
        else:
            st.error(f"❌ Failed to load schema: {schema_response.get('message', 'Unknown error')}")
    
    st.divider()
    
    # Database statistics
    st.subheader("Frontend Database")
    stats = db.get_stats()
    
    col1, col2 = st.columns(2)
    with col1:
        st.json({
            "Total Queries": stats['total_queries'],
            "Successful Queries": stats['successful_queries'],
            "Success Rate": f"{stats['success_rate']}%"
        })
    
    with col2:
        st.json({
            "Avg Execution Time": f"{stats['avg_execution_time']}ms",
            "Positive Feedback": stats['positive_feedback'],
            "Database": "In-Memory SQLite"
        })
    
    # Clear data button
    if st.button("🗑️ Clear Query Logs", type="secondary"):
        if st.button("Confirm Clear", type="primary"):
            # Reinitialize database
            db = db.__class__()
            st.success("✅ Query logs cleared!")
            st.rerun()

def main():
    """Main application."""
    # Apply theme
    apply_theme()
    
    # Render header
    render_header()
    
    # Render sidebar
    render_sidebar()
    
    # Render current tab
    current_tab = st.session_state.current_tab
    
    if current_tab == "Query":
        render_query_tab()
    elif current_tab == "Dashboard":
        render_dashboard_tab()
    elif current_tab == "Admin":
        render_admin_tab()

if __name__ == "__main__":
    main()