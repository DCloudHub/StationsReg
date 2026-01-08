import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import requests
import json
import os
from io import StringIO
import altair as alt
import matplotlib.pyplot as plt
import seaborn as sns

# Set page configuration
st.set_page_config(
    page_title="StationsReg Analytics",
    page_icon="🚆",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #1E3A8A;
    }
    .stButton > button {
        background-color: #1E3A8A;
        color: white;
        border: none;
        padding: 0.5rem 2rem;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

# App title and description
st.title("🚆 StationsReg Analytics Dashboard")
st.markdown("---")

# Initialize session state variables
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False
if 'df' not in st.session_state:
    st.session_state.df = None

# Sidebar for navigation and controls
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/984/984172.png", width=100)
    st.title("Navigation")
    
    # File uploader
    uploaded_file = st.file_uploader("📁 Upload CSV/Excel File", type=['csv', 'xlsx', 'xls'])
    
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            
            st.session_state.df = df
            st.session_state.data_loaded = True
            st.success(f"✅ Data loaded successfully! Shape: {df.shape}")
            
        except Exception as e:
            st.error(f"Error loading file: {e}")
    
    st.markdown("---")
    analysis_type = st.selectbox(
        "📊 Select Analysis Type",
        ["Data Overview", "Statistical Analysis", "Visualizations", "Predictive Models", "Export Results"]
    )
    
    st.markdown("---")
    st.info("ℹ️ Upload your data file to begin analysis.")

# Main content area
if st.session_state.data_loaded and st.session_state.df is not None:
    df = st.session_state.df
    
    if analysis_type == "Data Overview":
        st.header("📈 Data Overview")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Rows", df.shape[0])
        with col2:
            st.metric("Total Columns", df.shape[1])
        with col3:
            st.metric("Missing Values", df.isnull().sum().sum())
        
        st.subheader("Data Preview")
        st.dataframe(df.head(20), use_container_width=True)
        
        st.subheader("Column Information")
        col_info = pd.DataFrame({
            'Column': df.columns,
            'Data Type': df.dtypes.values,
            'Non-Null Count': df.count().values,
            'Unique Values': [df[col].nunique() for col in df.columns]
        })
        st.dataframe(col_info, use_container_width=True)
        
        # Show missing values
        if df.isnull().sum().sum() > 0:
            st.subheader("Missing Values Analysis")
            missing_df = pd.DataFrame(df.isnull().sum(), columns=['Missing Count'])
            missing_df['Percentage'] = (missing_df['Missing Count'] / len(df)) * 100
            missing_df = missing_df[missing_df['Missing Count'] > 0]
            st.dataframe(missing_df)
    
    elif analysis_type == "Statistical Analysis":
        st.header("📊 Statistical Analysis")
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if numeric_cols:
            selected_col = st.selectbox("Select Numeric Column", numeric_cols)
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Mean", f"{df[selected_col].mean():.2f}")
            with col2:
                st.metric("Median", f"{df[selected_col].median():.2f}")
            with col3:
                st.metric("Std Dev", f"{df[selected_col].std():.2f}")
            with col4:
                st.metric("Range", f"{df[selected_col].max() - df[selected_col].min():.2f}")
            
            # Correlation matrix
            st.subheader("Correlation Matrix")
            corr_matrix = df[numeric_cols].corr()
            fig, ax = plt.subplots(figsize=(10, 8))
            sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0, ax=ax)
            st.pyplot(fig)
        else:
            st.warning("No numeric columns found for statistical analysis.")
    
    elif analysis_type == "Visualizations":
        st.header("📊 Data Visualizations")
        
        plot_type = st.selectbox(
            "Select Plot Type",
            ["Histogram", "Scatter Plot", "Bar Chart", "Line Chart", "Box Plot"]
        )
        
        if plot_type == "Histogram":
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            if numeric_cols:
                selected_col = st.selectbox("Select Column", numeric_cols)
                fig = px.histogram(df, x=selected_col, title=f"Distribution of {selected_col}")
                st.plotly_chart(fig, use_container_width=True)
        
        elif plot_type == "Scatter Plot":
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            if len(numeric_cols) >= 2:
                col1, col2 = st.columns(2)
                with col1:
                    x_col = st.selectbox("X-axis", numeric_cols)
                with col2:
                    y_col = st.selectbox("Y-axis", numeric_cols)
                
                if x_col and y_col:
                    fig = px.scatter(df, x=x_col, y=y_col, title=f"{y_col} vs {x_col}")
                    st.plotly_chart(fig, use_container_width=True)
    
    elif analysis_type == "Export Results":
        st.header("💾 Export Results")
        
        export_format = st.selectbox("Select Export Format", ["CSV", "Excel", "JSON"])
        
        if export_format == "CSV":
            csv = df.to_csv(index=False)
            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name="analysis_results.csv",
                mime="text/csv"
            )
        elif export_format == "Excel":
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Results')
            st.download_button(
                label="📥 Download Excel",
                data=output.getvalue(),
                file_name="analysis_results.xlsx",
                mime="application/vnd.ms-excel"
            )
        
        # Generate report
        if st.button("📄 Generate Analysis Report"):
            with st.spinner("Generating report..."):
                report = f"""
                # Data Analysis Report
                
                ## Dataset Overview
                - **Total Records:** {df.shape[0]}
                - **Total Features:** {df.shape[1]}
                - **Data Types:**
                {df.dtypes.value_counts().to_string()}
                
                ## Basic Statistics
                {df.describe().to_string()}
                
                Report generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                """
                
                st.download_button(
                    label="📥 Download Report",
                    data=report,
                    file_name="analysis_report.md",
                    mime="text/markdown"
                )

else:
    # Welcome screen when no data is loaded
    st.info("👈 Please upload a data file using the sidebar to begin analysis.")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=100)
        st.subheader("Upload Data")
        st.write("CSV, Excel, or JSON formats")
    with col2:
        st.image("https://cdn-icons-png.flaticon.com/512/2103/2103655.png", width=100)
        st.subheader("Analyze")
        st.write("Statistical analysis and insights")
    with col3:
        st.image("https://cdn-icons-png.flaticon.com/512/2917/2917995.png", width=100)
        st.subheader("Visualize")
        st.write("Interactive charts and graphs")

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666;'>"
    "🚆 StationsReg Analytics Dashboard | Built with Streamlit"
    "</div>",
    unsafe_allow_html=True
)
