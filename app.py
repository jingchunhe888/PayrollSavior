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
    st.title("Payroll Savior 1.4")
    
    st.markdown('''v1.4 Release Notes:  
    1. Organized printing 
    2. 'To Review' download folder for in-out-in-out formats AND if there is an extra employee in Goldfine Timesheet.''')
    
    st.write("[View User Guide](https://docs.google.com/document/d/1QMZrcSBi4Cax1r3_MLoRC-QLfkkZThgMhR2kpejT_5U/edit?usp=sharing)")



    with st.expander("View All Previous Release Notes"):
        st.markdown('''  
        **v1.3**
        1. Checks whether Goldfine Timesheets has more employees than BLS Excel.  
        2. 'To Review' download folder for in-out-in-out formats.''')
        
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

    if uploaded_files:
        st.write(f"Uploaded {len(uploaded_files)} files")

        # Create a summary and process the files when the button is clicked
        if st.button("Summary"):
            old_stdout = sys.stdout
            new_stdout = io.StringIO()
            sys.stdout = new_stdout

            try:
                # Save uploaded files to the temp directory
                file_paths = save_uploaded_files(uploaded_files)

                # Process the files using the models function (adjust to your logic)
                models('temp')  # Assumes this function processes files in the 'temp' directory
                
                # After processing, delete the temp directory (commented out for now)
                # delete_temp_dir()  # Avoid deleting temp too early
            finally:
                sys.stdout = old_stdout

            if new_stdout.getvalue():
                st.text_area("Summary", new_stdout.getvalue(), height=400)

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
