import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# Define API endpoint
API_URL = "https://api.knoxxi.net/knoxxi-urinanalysis/process"

# Streamlit app title
st.title("Urinalysis Test Platform")

# Upload image section
st.subheader("Upload an Image")
uploaded_file = st.file_uploader("Choose an image file", type=["jpg", "jpeg", "png"])

# Results container in session state
if "results_table" not in st.session_state:
    st.session_state.results_table = []
if "detailed_results" not in st.session_state:
    st.session_state.detailed_results = {}

# Function to fetch data from API
def fetch_results(image):
    files = {"image": (image.name, image.getvalue(), image.type)}
    headers = {
        "Accept": "application/json",
        "User-Agent": "KnoxxiUrinalysis/1.0"
    }
    try:
        response = requests.post(API_URL, files=files, headers=headers, timeout=60)
        if response.status_code == 200:
            return response.json()  # Return full response
        elif response.status_code == 400:
            st.error(f"Error 400: {response.json().get('details', 'Invalid request')}")
        elif response.status_code == 422:
            st.error("Error 422: Unprocessable Entity. Please check the file format.")
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")
        return None
    except Exception as e:
        st.error(f"An unexpected error occurred: {str(e)}")
        return None

# Modal dialog function for viewing detailed results
@st.dialog("Detailed Results")
def view_details(record_id):
    detailed_result = st.session_state.detailed_results.get(record_id)
    if detailed_result:
        for test in detailed_result:
            parameter = list(test.keys())[0]
            st.markdown(f"### {parameter}: {test[parameter]}")
            st.markdown(f"**Interpretation:** {test['interpretation']}")
            st.markdown(f"**Clinical Significance:** {test['clinical_significance']}")
            st.markdown(f"**Follow-Up:** {test['follow_up']}")
    if st.button("Close"):
        st.rerun()

# Submit button
if st.button("Submit") and uploaded_file:
    with st.spinner("Processing your image. Please wait..."):
        api_response = fetch_results(uploaded_file)
        if api_response:
            # Extract basic details
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            record_id = len(st.session_state.results_table) + 1

            # Add to session state
            st.session_state.results_table.append({
                "ID": record_id,
                "Timestamp": timestamp,
            })
            # Store only the "results" dictionary for expanded view
            st.session_state.detailed_results[record_id] = api_response.get("results", [])

            st.success("Results added successfully!")
        else:
            st.error("Failed to process the image.")

# Display results in a simulated table layout
if st.session_state.results_table:
    st.subheader("Analysis Results")

    # Table headers
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        st.markdown("**ID**")
    with col2:
        st.markdown("**Timestamp**")
    with col3:
        st.markdown("**Action**")

    # Table rows
    for record in st.session_state.results_table:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            st.write(record["ID"])
        with col2:
            st.write(record["Timestamp"])
        with col3:
            if st.button(f"View Result", key=f"view-{record['ID']}"):
                view_details(record["ID"])
