import streamlit as st
import io
import os
import zipfile
import shutil
from models import *
from dataformat import *
from config import *
import sys

# Function to save uploaded files to a temporary directory
def save_uploaded_files(uploaded_files, temp_dir="temp"):
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    
    file_paths = []
    for uploaded_file in uploaded_files:
        file_path = os.path.join(temp_dir, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getvalue())  # Save each file's contents
        file_paths.append(file_path)
    return file_paths

# Function to delete the temp directory
def delete_temp_dir(temp_dir="temp"):
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)

# Main function for the Streamlit app
def main():
    st.title("Payroll Savior v1.4")
    
    st.markdown('''v1.4 Release Notes:  
    1. Output Box: Prints all errors based on file order.  
    2. Error checking folders:  
    a. If BLS has added or removed an employee.  
    b. If BLS forgot to add a value to the total column.  
    c. Fill sheet for employees with computation error, but leave computation errors blank.''')
    
    st.write("[View User Guide](https://docs.google.com/document/d/1QMZrcSBi4Cax1r3_MLoRC-QLfkkZThgMhR2kpejT_5U/edit?usp=sharing)")

    with st.expander("View All Previous Release Notes"):
        st.markdown('''  
        **v1.3**
        1. Checks whether Goldfine Timesheets has more employees than BLS Excel.  
        2. 'To Review' download folder for in-out-in-out formats.
        
        **v1.2:**  
        1. Supports Saturdays.  
        2. Supports hidden columns.  
        
        **v1.1:**  
        1. Handles wrong weekday headings for overtime computation.
        ''')

    # Upload multiple files
    uploaded_files = st.file_uploader(
        "Upload BLS Excel and Goldfine Timesheet CSV Files:",
        type=["csv", "xlsx"],
        accept_multiple_files=True
    )

    # Reset summary and download button if the number of uploaded files changes
    if 'file_count' not in st.session_state:
        st.session_state.file_count = 0

    if uploaded_files and len(uploaded_files) != st.session_state.file_count:
        st.session_state.file_count = len(uploaded_files)
        st.session_state.summary = ""
        st.session_state.show_download = False

    if uploaded_files:
        st.write(f"Uploaded {len(uploaded_files)} files")

        # Check if the "Summary" button is clicked
        if st.button("Summary"):
            # Clear previous summary
            st.session_state['summary'] = ""
            st.session_state.show_download = False
            
            old_stdout = sys.stdout
            new_stdout = io.StringIO()
            sys.stdout = new_stdout

            try:
                # Save uploaded files to the temp directory
                file_paths = save_uploaded_files(uploaded_files)

                # Process the files using the models function (adjust to your logic)
                models('temp')  # Assumes this function processes files in the 'temp' directory
            finally:
                sys.stdout = old_stdout

            # Store the summary output in session state
            st.session_state['summary'] = new_stdout.getvalue()
            st.session_state.show_download = True  # Enable download button after summary

        # Display the summary output if available
        if 'summary' in st.session_state and st.session_state['summary']:
            st.text_area("Summary", st.session_state['summary'], height=400)

        # Show download button only after summary is generated
        if 'show_download' in st.session_state and st.session_state.show_download:
            # Create a ZIP file with the processed files
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
                for root, _, files in os.walk('temp'):
                    for file in files:
                        file_path = os.path.join(root, file)
                        zipf.write(file_path, os.path.relpath(file_path, start='temp'))

            zip_buffer.seek(0)

            # Provide a download button for the ZIP file
            st.download_button(
                label="Download Filled Files",
                data=zip_buffer,
                file_name="BLS Payroll Results.zip",
                mime="application/zip"
            )

        # Optionally delete temp directory after download
        delete_temp_dir()

if __name__ == "__main__":
    main()
