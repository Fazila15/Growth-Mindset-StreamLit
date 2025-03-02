import streamlit as st
import pandas as pd
import plotly.express as px
import os
from sklearn.linear_model import LinearRegression
from io import BytesIO
import firebase_admin
from firebase_admin import credentials, firestore
import json


# Streamlit Secrets se Firebase credentials read karna
firebase_config = st.secrets["firebase"]

# Initialize Firebase (Check if already initialized)
db = None  # Global Firestore variable

if not firebase_admin._apps:
    try:
        cred = credentials.Certificate(firebase_config)  # Ensure this file exists
        firebase_admin.initialize_app(cred)
        db = firestore.client()
    except Exception as e:
        st.error(f"❌ Firebase Initialization Failed: {e}")
        db = None  # Ensure db is None if Firebase fails

st.set_page_config(page_title="Growth Mindset Web App", page_icon="🧠", layout="wide")
st.title("🧠 Growth Mindset Project Web App with Advanced Features 🧠")

# Sync Data to Firebase (Check if db is initialized)
if db:
    st.subheader("Collaborate in Real-Time:")
    if st.button("Sync Data to Firebase"):
        try:
            doc_ref = db.collection("growth_mindset").document("example_document")
            doc_ref.set({"message": "Test data synced!"})
            st.success("✅ Data synced to Firebase!")
        except Exception as e:
            st.error(f"❌ Failed to sync data: {e}")
else:
    st.warning("⚠️ Firebase is not initialized. Please check your credentials and try again.")

# Dark Mode Toggle
dark_mode = st.sidebar.checkbox("Enable Dark Mode")
if dark_mode:
    st.markdown("""
        <style>
            body, .stApp { background-color: #2E2E2E !important; color: white !important; }
            .stButton>button { background-color: #2D9CDB !important; color: white !important; }
            .stTextInput>div>div>input, .stFileUploader>div>div { background-color: #4F4F4F !important; color: white !important; }
        </style>
    """, unsafe_allow_html=True)

# User Authentication
st.sidebar.title("Authentication")
username = st.sidebar.text_input("Username")
password = st.sidebar.text_input("Password", type="password")
if username and password:
    st.sidebar.success("✅ Login successful!")
else:
    st.sidebar.warning("⚠️ Enter username and password")

# File Upload
df = None
uploaded_files = st.file_uploader("Upload CSV or Excel", type=["csv", "xlsx"], accept_multiple_files=False)
if uploaded_files:
    file_ext = os.path.splitext(uploaded_files.name)[-1].lower()
    try:
        if file_ext == ".csv":
            df = pd.read_csv(uploaded_files)
        elif file_ext == ".xlsx":
            df = pd.read_excel(uploaded_files, engine='openpyxl')
        st.success(f"✅ Successfully loaded {uploaded_files.name}")
    except Exception as e:
        st.error(f"❌ Error loading file: {str(e)}")

# Data Cleaning
df_cleaned = df.copy() if df is not None else None
if df_cleaned is not None:
    st.subheader("Data Cleaning Options:")
    if st.button("Remove Duplicates"):
        df_cleaned.drop_duplicates(inplace=True)
        st.success("✅ Duplicates Removed")

    # Predictive Model
    if st.checkbox("Run Predictive Model (Linear Regression)"):
        try:
            feature_col, target_col = st.selectbox("Feature Column", df_cleaned.columns), st.selectbox("Target Column", df_cleaned.columns)
            model = LinearRegression()
            model.fit(df_cleaned[[feature_col]], df_cleaned[target_col])
            df_cleaned['Predictions'] = model.predict(df_cleaned[[feature_col]])
            st.write(df_cleaned[['Predictions']])
        except Exception as e:
            st.error("❌ Ensure numerical data in selected columns.")

    # Visualizations
    st.subheader("Visualizations")
    plot_type = st.radio("Select Plot Type", ["Bar Chart", "Scatter Plot", "Pie Chart", "Line Chart"])
    if plot_type and len(df_cleaned.columns) >= 2:
        col_x, col_y = df_cleaned.columns[:2]
        try:
            if plot_type == "Bar Chart":
                st.plotly_chart(px.bar(df_cleaned, x=col_x, y=col_y, title="Bar Chart"))
            elif plot_type == "Scatter Plot":
                st.plotly_chart(px.scatter(df_cleaned, x=col_x, y=col_y, title="Scatter Plot"))
            elif plot_type == "Pie Chart":
                st.plotly_chart(px.pie(df_cleaned, names=col_x, values=col_y, title="Pie Chart"))
            elif plot_type == "Line Chart":
                st.plotly_chart(px.line(df_cleaned, x=col_x, y=col_y, title="Line Chart"))
        except Exception as e:
            st.error("❌ Error generating visualization: Ensure correct data format.")

    # Exporting Options
    st.subheader("Export Data")
    export_type = st.radio("Export As", ["CSV", "Excel"])
    if st.button(f"Export {export_type}"):
        buffer = BytesIO()
        if export_type == "CSV":
            df_cleaned.to_csv(buffer, index=False)
            st.download_button("Download CSV", buffer.getvalue(), f"{uploaded_files.name}.csv")
        else:
            df_cleaned.to_excel(buffer, engine='openpyxl', index=False)
            st.download_button("Download Excel", buffer.getvalue(), f"{uploaded_files.name}.xlsx")

    # Sync Data to Firebase
    if db:
        if st.button("Sync Data to Firebase"):
            try:
                doc_ref = db.collection("growth_mindset").document(uploaded_files.name)
                doc_ref.set({"data": df_cleaned.to_dict(orient='records')})
                st.success("✅ Data synced to Firebase!")
            except Exception as e:
                st.error(f"❌ Error syncing data: {e}")
    else:
        st.warning("⚠️ Cannot sync data. Firebase is not initialized.")

# Sidebar Navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Data Cleaning", "Visualization", "Analysis"])
if page == "Data Cleaning":
    st.write("Perform data cleaning operations here.")
elif page == "Visualization":
    st.write("Create advanced visualizations here.")
elif page == "Analysis":
    st.write("Run predictive models and analysis here.")

st.write("🚀 Thank you for using the Growth Mindset Web App!")
