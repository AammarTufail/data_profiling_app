import streamlit as st
import pandas as pd
import seaborn as sns
from ydata_profiling import ProfileReport
import io

import streamlit.components.v1 as components

st.set_page_config(page_title="Data Profiling App by Codanics.com", layout="wide")

st.title("📊 Data Profiling App by Codanics.com")
st.markdown("Upload your dataset or try with sample data to generate an automated profiling report")

# Sidebar for sample datasets
st.sidebar.header("Sample Datasets")
sample_datasets = {
    "Diamonds": "diamonds",
    "Tips": "tips", 
    "Flights": "flights",
    "Iris": "iris",
    "Titanic": "titanic"
}

selected_sample = st.sidebar.selectbox("Choose a sample dataset:", ["None"] + list(sample_datasets.keys()))

# Main content area
col1, col2 = st.columns([1, 2])

with col1:
    st.header("Data Upload")
    
    # File uploader
    uploaded_file = st.file_uploader(
        "Drag and drop your CSV file here",
        type=['csv'],
        help="Upload a CSV file to generate profiling report"
    )

df = None

# Load data based on user choice
if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        st.success(f"✅ File uploaded successfully! Shape: {df.shape}")
    except Exception as e:
        st.error(f"Error reading file: {str(e)}")

elif selected_sample != "None":
    try:
        df = sns.load_dataset(sample_datasets[selected_sample])
        st.info(f"📋 Loaded sample dataset: {selected_sample}")
        st.success(f"Shape: {df.shape}")
    except Exception as e:
        st.error(f"Error loading sample dataset: {str(e)}")

# Display data preview and generate report
if df is not None:
    with col1:
        st.subheader("Data Preview")
        st.dataframe(df.head(10))
    
    with col2:
        st.subheader("Profiling Report")
        
        # Generate profiling report
        with st.spinner("Generating profiling report..."):
            try:
                dataset_name = selected_sample if selected_sample != "None" else "Uploaded Dataset"
                profile = ProfileReport(
                    df, 
                    title=f"Profiling Report - {dataset_name}",
                    explorative=True
                )
                
                # Convert to HTML
                html_report = profile.to_html()
                
                # Display in iframe
                components.html(html_report, height=800, scrolling=True)
                
                # Download button
                st.download_button(
                    label="📥 Download Report as HTML",
                    data=html_report,
                    file_name=f"{dataset_name.lower().replace(' ', '_')}_profiling_report.html",
                    mime="text/html"
                )
                
            except Exception as e:
                st.error(f"Error generating report: {str(e)}")

else:
    st.info("👆 Please upload a CSV file or select a sample dataset to get started")