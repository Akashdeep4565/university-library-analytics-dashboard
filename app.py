import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------

st.set_page_config(
    page_title="Central Library Analytics Dashboard",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------
# CUSTOM CSS
# ---------------------------------------------------

st.markdown("""
<style>
    /* Title styling */
    .title-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 20px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        text-align: center;
    }
    
    .title-container h1 {
        margin: 0;
        font-size: 2.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    /* KPI Cards */
    .kpi-card {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        text-align: center;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        border-left: 4px solid #667eea;
        margin: 0.5rem 0;
    }
    
    .kpi-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }
    
    .kpi-icon {
        font-size: 2rem;
        margin-bottom: 0.5rem;
    }
    
    .kpi-value {
        font-size: 2rem;
        font-weight: bold;
        color: #333;
        margin: 0.5rem 0;
    }
    
    .kpi-label {
        font-size: 0.9rem;
        color: #666;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Section headers */
    .section-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.8rem 1.5rem;
        border-radius: 10px;
        margin: 2rem 0 1rem 0;
        font-size: 1.2rem;
        font-weight: bold;
        box-shadow: 0 4px 10px rgba(102, 126, 234, 0.3);
    }
    
    /* Chart containers */
    .chart-container {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
    
    /* Insights box */
    .insight-box {
        background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
        padding: 1.5rem;
        border-radius: 15px;
        border-left: 5px solid #667eea;
        margin: 1rem 0;
    }
    
    .insight-item {
        display: flex;
        align-items: center;
        margin: 0.5rem 0;
        padding: 0.5rem;
        background: white;
        border-radius: 8px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    
    .insight-icon {
        font-size: 1.5rem;
        margin-right: 1rem;
    }
    
</style>

""", unsafe_allow_html=True)

# ---------------------------------------------------
# TITLE
# ---------------------------------------------------

st.markdown("""
<div class="title-container">
    <h1>📚 University Central Library Analytics Dashboard</h1>
    <p>Real-time insights into library usage patterns, book borrowing trends, and student engagement</p>
</div>
""", unsafe_allow_html=True)
# Add this to your existing CSS section
st.markdown("""
<style>
    /* Fix container overlapping */
    .stPlotlyChart {
        margin-bottom: 20px !important;
    }
    
    /* Add spacing between columns */
    [data-testid="column"] {
        padding: 0 15px !important;
    }
    
    /* Ensure charts don't overflow */
    .js-plotly-plot, .plot-container {
        max-width: 100% !important;
        overflow: hidden !important;
    }
    
    /* Section spacing */
    .section-header {
        margin-top: 30px !important;
        margin-bottom: 20px !important;
    }
    
    /* Row spacing */
    [data-testid="stHorizontalBlock"] {
        margin-bottom: 20px !important;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------
# LOAD DATA
# ---------------------------------------------------

@st.cache_data(ttl=3600)
def load_data():
    library_df = pd.read_csv("processed_library_data.csv")
    study_df = pd.read_csv("processed_study_data.csv")
    
    # Convert date columns if needed
    if 'Issue Date' in library_df.columns:
        library_df['Issue Date'] = pd.to_datetime(library_df['Issue Date'])
    if 'Entry Time' in library_df.columns:
        library_df['Entry Time'] = pd.to_datetime(library_df['Entry Time'])
    
    return library_df, study_df

library_df, study_df = load_data()

# Load and clean data
library_df = pd.read_csv("processed_library_data.csv")
study_df = pd.read_csv("processed_study_data.csv")

# Clean study duration - remove/replace negative values
study_df['Study_Duration_Hours'] = study_df['Study_Duration_Hours'].apply(lambda x: abs(x) if x < 0 else x)

# OR if you want to investigate negative values
negative_mask = study_df['Study_Duration_Hours'] < 0
if negative_mask.sum() > 0:
    st.warning(f"Found {negative_mask.sum()} negative study hours. They have been converted to positive values.")
    study_df.loc[negative_mask, 'Study_Duration_Hours'] = study_df.loc[negative_mask, 'Study_Duration_Hours'].abs()

# ---------------------------------------------------
# SIDEBAR FILTERS
# ---------------------------------------------------

with st.sidebar:
    st.markdown("## 🎯 Dashboard Controls")
    st.markdown("---")
    
    # View Mode Selection
    st.markdown("### 📊 View Mode")
    view_mode = st.radio(
        "Select view mode",
        ["🏢 All Departments", "🏛️ Single Department"],
        help="Choose between overview or detailed department view"
    )
    
    # Department Selection
    if view_mode == "🏛️ Single Department":
        st.markdown("---")
        
        # Search box for quick department find
        department_search = st.text_input(
            "🔍 Search department",
            placeholder="Type to search...",
            help="Filter departments by name"
        )
        
        # Get department list
        all_depts = sorted(library_df['Department'].unique())
        
        # Filter based on search
        if department_search:
            filtered_depts = [d for d in all_depts if department_search.lower() in d.lower()]
        else:
            filtered_depts = all_depts
        
        # Handle no results
        if not filtered_depts:
            st.warning("🚫 No departments found matching your search")
            department = None
            filtered_library = pd.DataFrame()
            filtered_study = pd.DataFrame()
        else:
            department = st.selectbox(
                "Choose department",
                filtered_depts,
                help="Select a specific department to analyze"
            )
            # FILTER DATA - This is the key part
            filtered_library = library_df[library_df['Department'] == department].copy()
            filtered_study = study_df[study_df['Department'] == department].copy()
        
        st.success(f"✅ Showing: **{department}**" if department else "⚠️ No department selected")
            
    else:
        # Show all departments
        department = 'All Departments'
        # FILTER DATA - Show all data
        filtered_library = library_df.copy()
        filtered_study = study_df.copy()
        st.info("📊 Showing: **All Departments**")
    
    st.markdown("---")
    
    # Quick Statistics (only if data exists)
    if len(filtered_library) > 0:
        st.markdown("### 📊 Quick Statistics")
        
        # Calculate metrics
        total_books = len(filtered_library)
        total_study = len(filtered_study)
        unique_students = filtered_library['Student ID'].nunique()
        avg_borrow = filtered_library['Borrow_Days'].mean()
        avg_study = filtered_study['Study_Duration_Hours'].mean() if len(filtered_study) > 0 else 0
        
        # Display metrics
        col1, col2 = st.columns(2)
        with col1:
            st.metric("📖 Books", f"{total_books:,}")
            st.metric("⏱️ Avg Days", f"{avg_borrow:.1f}")
        with col2:
            st.metric("👥 Students", f"{unique_students:,}")
            st.metric("📝 Study Logs", f"{total_study:,}")
        
        # Top category for single department view
        if view_mode == "🏛️ Single Department" and department:
            if 'Book Category' in filtered_library.columns:
                top_cat = filtered_library['Book Category'].value_counts().idxmax()
                st.markdown(f"**🏆 Top Category:** {top_cat}")
    
    st.markdown("---")
    
    # Export Options
    st.markdown("### 📥 Export Data")
    
    col1, col2 = st.columns(2)
    with col1:
        if len(filtered_library) > 0:
            csv_lib = filtered_library.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📖 Library",
                data=csv_lib,
                file_name=f"library_data_{department}.csv",
                mime="text/csv",
                use_container_width=True
            )
        else:
            st.button("📖 Library", disabled=True, use_container_width=True)
    
    with col2:
        if len(filtered_study) > 0:
            csv_study = filtered_study.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📝 Study",
                data=csv_study,
                file_name=f"study_data_{department}.csv",
                mime="text/csv",
                use_container_width=True
            )
        else:
            st.button("📝 Study", disabled=True, use_container_width=True)
    
    st.markdown("---")
    
    # Reset Button
    if st.button("🔄 Reset All Filters", use_container_width=True, type="primary"):
        # Clear session state and rerun
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
    
    st.markdown(f"*🕒 Updated: {datetime.now().strftime('%H:%M')}*")

# ---------------------------------------------------
# MAIN CONTENT - Only show if data exists
# ---------------------------------------------------

if len(filtered_library) == 0:
    st.warning("⚠️ No data available for the selected filters. Please adjust your selection.")
    st.stop()

# ---------------------------------------------------
# KPI SECTION
# ---------------------------------------------------

# Calculate KPI metrics
total_books = len(filtered_library)
avg_borrow = round(filtered_library['Borrow_Days'].mean(), 2)
avg_study = round(filtered_study['Study_Duration_Hours'].mean(), 2) if len(filtered_study) > 0 else 0
top_category = filtered_library['Book Category'].value_counts().idxmax() if 'Book Category' in filtered_library.columns else "N/A"
total_students = filtered_library['Student ID'].nunique()

st.markdown('<div class="section-header">📊 Key Performance Indicators</div>', unsafe_allow_html=True)

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-icon">📚</div>
        <div class="kpi-value">{total_books:,}</div>
        <div class="kpi-label">Books Issued</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="kpi-card" style="border-left: 4px solid #f5576c;">
        <div class="kpi-icon">⏱️</div>
        <div class="kpi-value">{avg_borrow}</div>
        <div class="kpi-label">Avg Borrow Days</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="kpi-card" style="border-left: 4px solid #4facfe;">
        <div class="kpi-icon">📖</div>
        <div class="kpi-value">{avg_study}</div>
        <div class="kpi-label">Avg Study Hours</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="kpi-card" style="border-left: 4px solid #43e97b;">
        <div class="kpi-icon">🏆</div>
        <div class="kpi-value" style="font-size: 1.2rem;">{top_category[:20]}</div>
        <div class="kpi-label">Top Category</div>
    </div>
    """, unsafe_allow_html=True)

with col5:
    st.markdown(f"""
    <div class="kpi-card" style="border-left: 4px solid #fa8231;">
        <div class="kpi-icon">👥</div>
        <div class="kpi-value">{total_students:,}</div>
        <div class="kpi-label">Unique Students</div>
    </div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------
# CHART ROW 1 - Department & Category Analysis
# ---------------------------------------------------

st.markdown('<div class="section-header">📈 Department & Category Analysis</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2, gap="large")  # Added gap between columns

with col1:
    # Department Usage Chart
    if view_mode == "🏢 All Departments":
        dept_usage = (
            library_df['Department']
            .value_counts()
            .reset_index()
        )
        dept_usage.columns = ['Department', 'Usage Count']
        dept_usage = dept_usage.sort_values('Usage Count', ascending=True).tail(10)
        
        fig1 = px.bar(
            dept_usage,
            x='Usage Count',
            y='Department',
            orientation='h',
            title='Top 10 Departments by Library Usage',
            color='Usage Count',
            color_continuous_scale='Blues',
            text='Usage Count'
        )
        
        fig1.update_traces(
            textposition='outside',
            marker_line_color='white',
            marker_line_width=1.5,
            opacity=0.9
        )
        
        fig1.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_family="Arial",
            title_font_size=16,
            showlegend=False,
            height=400,  # Fixed height
            margin=dict(l=0, r=30, t=50, b=0)
        )
        
    else:
        # Single department - Show top 10 with selected highlighted
        dept_usage = (
            library_df['Department']
            .value_counts()
            .reset_index()
        )
        dept_usage.columns = ['Department', 'Usage Count']
        dept_usage = dept_usage.sort_values('Usage Count', ascending=True)
        
        dept_usage['Rank'] = range(1, len(dept_usage) + 1)
        selected_rank = dept_usage[dept_usage['Department'] == department]['Rank'].values[0]
        total_depts = len(dept_usage)
        
        # Show only top 12 departments (less to prevent overlap)
        top_display = dept_usage.tail(12).copy()
        if department not in top_display['Department'].values:
            dept_row = dept_usage[dept_usage['Department'] == department]
            top_display = pd.concat([top_display, dept_row])
        
        # Create color array
        colors = ['#e0e0e0'] * len(top_display)
        dept_idx = top_display[top_display['Department'] == department].index
        if len(dept_idx) > 0:
            colors[top_display.index.get_loc(dept_idx[0])] = '#667eea'
        
        fig1 = go.Figure()
        fig1.add_trace(go.Bar(
            y=top_display['Department'],
            x=top_display['Usage Count'],
            orientation='h',
            marker_color=colors,
            text=top_display['Usage Count'],
            textposition='outside',
            textfont=dict(
                color=['#667eea' if c == '#667eea' else '#999' for c in colors],
                size=[13 if c == '#667eea' else 10 for c in colors]
            ),
            marker_line_color='white',
            marker_line_width=1
        ))
        
        fig1.update_layout(
            title=f'Department Usage - {department}<br><sup>Rank: #{selected_rank} of {total_depts}</sup>',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            title_font_size=14,
            height=400,  # Fixed height
            margin=dict(l=0, r=50, t=60, b=0),
            showlegend=False,
            xaxis_title="Number of Visits"
        )
    
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    # Book Categories Distribution
    if view_mode == "🏢 All Departments":
        category_data = (
            library_df['Book Category']
            .value_counts()
            .head(8)
            .reset_index()
        )
    else:
        category_data = (
            filtered_library['Book Category']
            .value_counts()
            .head(8)
            .reset_index()
        )
    
    category_data.columns = ['Book Category', 'Count']
    total = category_data['Count'].sum()
    
    colors = ['#667eea', '#764ba2', '#f5576c', '#4facfe', '#43e97b', '#fa8231', '#f7b731', '#20bf6b']
    
    fig2 = go.Figure(data=[go.Pie(
        labels=category_data['Book Category'],
        values=category_data['Count'],
        hole=0.5,
        marker=dict(
            colors=colors[:len(category_data)],
            line=dict(color='white', width=2)
        ),
        textinfo='label+percent',
        textposition='outside',
        textfont=dict(size=11),
        hovertemplate='%{label}<br>%{value:,} books<br>%{percent}<extra></extra>'
    )])
    
    fig2.update_layout(
        title=f'Book Categories Distribution<br><sup>{"" if view_mode == "All Departments" else department}</sup>',
        showlegend=False,
        height=400,  # Fixed height
        margin=dict(l=20, r=80, t=60, b=20),
        annotations=[dict(
            text=f'Total<br>{total:,}',
            x=0.5, y=0.5,
            font=dict(size=14),
            showarrow=False
        )]
    )
    
    st.plotly_chart(fig2, use_container_width=True)

# Add spacing between rows
st.markdown("<br>", unsafe_allow_html=True)

# ---------------------------------------------------
# CHART ROW 2 - Temporal Analysis
# ---------------------------------------------------

st.markdown('<div class="section-header">📅 Temporal Analysis</div>', unsafe_allow_html=True)

col3, col4 = st.columns(2, gap="large")  # Added gap

with col3:
    # Monthly Trend
    if view_mode == "🏢 All Departments":
        monthly_usage = (
            library_df.groupby('Month')
            .size()
            .reset_index(name='Usage')
        )
    else:
        monthly_usage = (
            filtered_library.groupby('Month')
            .size()
            .reset_index(name='Usage')
        )
    
    fig3 = go.Figure()
    
    fig3.add_trace(go.Scatter(
        x=monthly_usage['Month'],
        y=monthly_usage['Usage'],
        mode='lines+markers',
        name='Usage',
        fill='tozeroy',
        fillcolor='rgba(102, 126, 234, 0.2)',
        line=dict(color='#667eea', width=3),
        marker=dict(size=8, color='#764ba2')
    ))
    
    fig3.update_layout(
        title=f'Monthly Library Usage Trend<br><sup>{"" if view_mode == "All Departments" else department}</sup>',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        title_font_size=14,
        height=380,  # Slightly smaller to prevent overlap
        margin=dict(l=0, r=0, t=60, b=0),
        hovermode='x unified'
    )
    
    st.plotly_chart(fig3, use_container_width=True)

with col4:
    # Study Duration by Department
    if view_mode == "🏢 All Departments":
        study_duration = (
            study_df.groupby('Department')['Study_Duration_Hours']
            .mean()
            .reset_index()
            .sort_values('Study_Duration_Hours', ascending=True)
            .tail(10)
        )
        
        if len(study_duration) > 0:
            fig4 = px.bar(
                study_duration,
                x='Study_Duration_Hours',
                y='Department',
                orientation='h',
                title='Top 10 Departments by Avg Study Hours',
                color='Study_Duration_Hours',
                color_continuous_scale='Viridis',
                text='Study_Duration_Hours'
            )
            
            fig4.update_traces(
                texttemplate='%{text:.1f} hrs',
                textposition='outside'
            )
            
            fig4.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                title_font_size=16,
                height=380,
                margin=dict(l=0, r=30, t=50, b=0),
                showlegend=False,
                coloraxis_showscale=False
            )
            
            st.plotly_chart(fig4, use_container_width=True)
    
    else:
        # Single department - Comparison with university average
        if len(filtered_study) > 0:
            dept_avg = filtered_study['Study_Duration_Hours'].mean()
            uni_avg = study_df['Study_Duration_Hours'].mean()
            
            comparison_data = pd.DataFrame({
                'Category': ['University Average', department],
                'Study Hours': [uni_avg, dept_avg]
            })
            
            colors_bar = ['#95a5a6', '#667eea']
            
            fig4 = go.Figure()
            
            fig4.add_trace(go.Bar(
                x=comparison_data['Category'],
                y=comparison_data['Study Hours'],
                marker_color=colors_bar,
                text=comparison_data['Study Hours'].round(1),
                textposition='outside',
                textfont=dict(size=14),
                width=0.4
            ))
            
            fig4.add_hline(
                y=uni_avg,
                line_dash="dash",
                line_color="red",
                annotation_text=f"Uni Avg: {uni_avg:.1f}h",
                annotation_position="top right"
            )
            
            fig4.update_layout(
                title=f'Study Duration - {department} vs University Average',
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                title_font_size=14,
                height=380,
                margin=dict(l=0, r=0, t=50, b=0),
                showlegend=False,
                yaxis_title="Hours",
                yaxis=dict(range=[0, max(dept_avg, uni_avg) * 1.3])
            )
            
            st.plotly_chart(fig4, use_container_width=True)
            
            diff = dept_avg - uni_avg
            if diff > 0:
                st.success(f"📈 {department} studies **{diff:.1f} hours more** than university average")
            else:
                st.warning(f"📉 {department} studies **{abs(diff):.1f} hours less** than university average")
        else:
            st.info(f"No study data available for {department}")

# Add spacing between rows
st.markdown("<br>", unsafe_allow_html=True)


# ---------------------------------------------------
# PEAK HOUR & BORROW ANALYSIS
# ---------------------------------------------------

st.markdown('<div class="section-header">⏰ Occupancy & Borrowing Patterns</div>', unsafe_allow_html=True)

col5, col6 = st.columns(2)

with col5:
    # Peak Hour Analysis
    if 'Entry_Hour' in filtered_study.columns and len(filtered_study) > 0:
        peak_hours = (
            filtered_study['Entry_Hour']
            .value_counts()
            .sort_index()
            .reset_index()
        )
        peak_hours.columns = ['Hour', 'Entries']
        
        fig5 = go.Figure()
        
        fig5.add_trace(go.Scatter(
            x=peak_hours['Hour'],
            y=peak_hours['Entries'],
            mode='lines+markers',
            fill='tozeroy',
            fillcolor='rgba(67, 233, 123, 0.2)',
            line=dict(color='#43e97b', width=3),
            marker=dict(
                size=10,
                color=peak_hours['Entries'],
                colorscale='Viridis',
                showscale=False
            )
        ))
        
        # Add peak hour annotation
        if len(peak_hours) > 0:
            peak_hour = peak_hours.loc[peak_hours['Entries'].idxmax()]
            fig5.add_annotation(
                x=peak_hour['Hour'],
                y=peak_hour['Entries'],
                text=f"Peak: {int(peak_hour['Hour'])}:00<br>{int(peak_hour['Entries'])} entries",
                showarrow=True,
                arrowhead=2,
                arrowsize=1,
                arrowwidth=2,
                arrowcolor="#636e72",
                ax=40,
                ay=-40,
                font=dict(size=11)
            )
        
        fig5.update_layout(
            title=f'Peak Library Occupancy Hours {"" if view_mode == "All Departments" else "- " + department}',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            title_font_size=18,
            height=400,
            margin=dict(l=0, r=0, t=40, b=0),
            xaxis=dict(tickmode='linear', dtick=1),
            hovermode='x unified'
        )
        
        st.plotly_chart(fig5, use_container_width=True)
    else:
        st.info("No entry hour data available for this selection")

with col6:
    # Borrow Duration Distribution
    if len(filtered_library) > 0:
        fig6 = px.histogram(
            filtered_library,
            x='Borrow_Days',
            nbins=30,
            title=f'Borrow Duration Distribution {"" if view_mode == "All Departments" else "- " + department}',
            color_discrete_sequence=['#667eea'],
            opacity=0.8,
            marginal='box'
        )
        
        fig6.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            title_font_size=18,
            height=400,
            margin=dict(l=0, r=0, t=40, b=0),
            bargap=0.1
        )
        
        # Add mean line
        mean_borrow = filtered_library['Borrow_Days'].mean()
        fig6.add_vline(
            x=mean_borrow,
            line_dash="dash",
            line_color="red",
            annotation_text=f"Mean: {mean_borrow:.1f} days",
            annotation_position="top"
        )
        
        st.plotly_chart(fig6, use_container_width=True)
    else:
        st.info("No borrow duration data available for this selection")

# ---------------------------------------------------
# INSIGHTS SECTION
# ---------------------------------------------------

st.markdown('<div class="section-header">💡 Key Insights & Recommendations</div>', unsafe_allow_html=True)

if view_mode == "🏢 All Departments":
    top_dept = library_df['Department'].value_counts().idxmax()
    top_dept_count = library_df['Department'].value_counts().max()
    top_cat = library_df['Book Category'].value_counts().idxmax()
    top_cat_count = library_df['Book Category'].value_counts().max()
    
    tab1, tab2 = st.tabs(["📊 Key Findings", "🎯 Recommendations"])
    
    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            with st.container(border=True):
                st.metric("🏆 Most Active Department", top_dept)
                st.caption(f"Total visits: {top_dept_count:,}")
        
        with col2:
            with st.container(border=True):
                st.metric("📚 Most Borrowed Category", top_cat)
                st.caption(f"Total books: {top_cat_count:,}")
        
        col3, col4 = st.columns(2)
        with col3:
            with st.container(border=True):
                st.markdown("⏰ **Peak Hours**")
                st.markdown("Afternoon & Evening (14:00-17:00)")
        
        with col4:
            with st.container(border=True):
                st.markdown("📈 **Usage Pattern**")
                st.markdown("Increases during exam periods")
    
    with tab2:
        st.markdown("### Actionable Recommendations")
        
        with st.expander("📖 Stock Management", expanded=True):
            st.markdown(f"- Increase **{top_cat}** inventory by 20%")
            st.markdown("- Add more copies of high-demand books")
            st.markdown("- Regular stock auditing for popular categories")
        
        with st.expander("👥 Staffing & Operations"):
            st.markdown("- Add 2 staff members during peak hours (14:00-17:00)")
            st.markdown("- Extend library hours during exam season")
            st.markdown("- Implement self-checkout kiosks")
        
        with st.expander("💻 Digital Resources"):
            st.markdown("- Promote e-resources for Engineering departments")
            st.markdown("- Create online reservation system")
            st.markdown("- Develop mobile app for notifications")

else:
    dept_books = len(filtered_library)
    dept_study_avg = filtered_study['Study_Duration_Hours'].mean() if len(filtered_study) > 0 else 0
    top_cat = filtered_library['Book Category'].value_counts().idxmax() if len(filtered_library) > 0 else "N/A"
    top_cat_count = filtered_library['Book Category'].value_counts().max() if len(filtered_library) > 0 else 0
    unique_students = filtered_library['Student ID'].nunique() if len(filtered_library) > 0 else 0
    uni_avg_study = study_df['Study_Duration_Hours'].mean()
    
    st.markdown(f"### 📊 {department} Department Analysis")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        with st.container(border=True):
            st.metric("📖 Books Issued", f"{dept_books:,}")
    
    with col2:
        with st.container(border=True):
            st.metric("👥 Students", f"{unique_students:,}")
    
    with col3:
        with st.container(border=True):
            st.metric("🏆 Top Category", top_cat)
            st.caption(f"Count: {top_cat_count:,}")
    
    with col4:
        with st.container(border=True):
            st.metric("⏱️ Avg Study Hours", f"{dept_study_avg:.1f}")
            delta = dept_study_avg - uni_avg_study
            st.caption(f"{'📈' if delta > 0 else '📉'} {abs(delta):.1f} hrs vs university avg")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🎯 Recommendations")
        st.info(f"📚 Increase **{top_cat}** stock for {department} students")
        st.success(f"⏰ Adjust hours based on {department} peak usage times")
        st.warning("💡 Create specialized reading lists for coursework")
    
    with col2:
        st.markdown("### 📈 Trends")
        st.info(f"📊 Monitor monthly borrowing patterns for {department}")
        st.success("🎯 Track category preferences changes over time")
        st.warning("📱 Consider department-specific digital resources")

# ---------------------------------------------------
# DATA EXPLORER
# ---------------------------------------------------

st.markdown('<div class="section-header">🔍 Data Explorer</div>', unsafe_allow_html=True)

tab1, tab2 = st.tabs(["📖 Library Records", "📝 Study Records"])

with tab1:
    st.markdown(f"*Showing records for **{department}***")
    st.dataframe(
        filtered_library.head(100),
        use_container_width=True,
        hide_index=True
    )

with tab2:
    st.markdown(f"*Showing records for **{department}***")
    
    # Remove redundant Date column from dashboard display
    study_display = filtered_study.drop(
        columns=['Date'],
        errors='ignore'
    )
    
    st.dataframe(
        study_display.head(100),
        use_container_width=True,
        hide_index=True
    )

# ---------------------------------------------------
# FOOTER
# ---------------------------------------------------

st.markdown("---")
st.markdown(f"""
<div style="text-align: center; color: #666; padding: 1rem;">
    <p>📚 University Central Library Analytics Dashboard | © {datetime.now().year}</p>
    <p style="font-size: 0.8rem;">Data refreshed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
</div>
""", unsafe_allow_html=True)