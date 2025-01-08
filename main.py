import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# Define API endpoint
API_URL = "https://api.knoxxi.net/knoxxi-urinanalysis/process"

# Streamlit app title
st.title("Urinalysis Test Platform")

# Upload image section
st.header("Upload an Image")
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

# Submit button
if st.button("Submit") and uploaded_file:
    with st.spinner("Processing your image. Please wait..."):
        api_response = fetch_results(uploaded_file)
        if api_response:
            # Extract basic details
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            record_id = len(st.session_state.results_table) + 1
            result_summary = "Success" if "results" in api_response else "Error"

            # Add to session state
            st.session_state.results_table.append({
                "ID": record_id,
                "Timestamp": timestamp,
                "Summary": result_summary,
            })
            # Store only the "results" dictionary for expanded view
            st.session_state.detailed_results[record_id] = api_response.get("results", [])
        else:
            st.error("Failed to process the image.")

# Display results table
if st.session_state.results_table:
    st.header("Analysis Results")

    # Create a DataFrame for display
    df = pd.DataFrame(st.session_state.results_table)
    
    # Select only the required columns and reset the index to start fresh
    df = df[["ID", "Timestamp", "Summary"]]
    
    # Create a new DataFrame that ignores the index
    df_no_index = pd.DataFrame(df.values, columns=df.columns)

    # Display the table
    st.table(df_no_index)
    

    # Expanded view for detailed results
    st.markdown("---")
    st.subheader("Detailed Results")
    for record in st.session_state.results_table:
        record_id = record["ID"]
        detailed_result = st.session_state.detailed_results.get(record_id)
        if detailed_result:
            with st.expander(f"Results for ID {record_id}"):
                for test in detailed_result:
                    parameter = list(test.keys())[0]  # Parameter name (e.g., "urobilinogen", "bilirubin")
                    st.markdown(f"### {parameter}: {test[parameter]}")
                    st.markdown(f"**Interpretation:** {test['interpretation']}")
                    st.markdown(f"**Clinical Significance:** {test['clinical_significance']}")
                    st.markdown(f"**Follow-Up:** {test['follow_up']}")
