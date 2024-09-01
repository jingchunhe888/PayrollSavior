import streamlit as st
from models import *
import io
import zipfile
from dataformat import *
from config import *


def save_uploaded_files(
        uploaded_files: list[st.runtime.uploaded_file_manager.UploadedFile], 
        temp_dir: str = "temp"
    ) -> None:
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)

    file_paths = []
    for uploaded_file in uploaded_files:
        file_path = os.path.join(temp_dir, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getvalue())
        file_paths.append(file_path)


def delete_temp_dir(temp_dir: str = "temp") -> None:
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)


def main():
    st.title("Payroll Savior")

    uploaded_files = st.file_uploader(
        "Upload Excel and CSV Files:",
        type=["csv", "xlsx"],
        accept_multiple_files=True
    )

    st.session_state.uploaded_files = uploaded_files
    st.write(f"Uploaded {len(uploaded_files)} files")

    if st.button("Summary") and 'uploaded_files' in st.session_state:
        old_stdout = sys.stdout
        new_stdout = io.StringIO()
        sys.stdout = new_stdout

        try:
            save_uploaded_files(uploaded_files)
            models('temp')
            delete_temp_dir()
        finally:
            sys.stdout = old_stdout

        if new_stdout:
            st.text_area("Summary", new_stdout.getvalue(), height=400)

        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk('temp'):
                for file in files:
                    file_path = os.path.join(root, file)
                    name = os.path.relpath(file_path, start='temp')
                    zipf.write(file_path, name)

        zip_buffer.seek(0)
            
        st.download_button(
            label="Download ZIP",
            data=zip_buffer,
            file_name="results.zip",
            mime="application/zip"
        )


if __name__ == "__main__":
    main()
