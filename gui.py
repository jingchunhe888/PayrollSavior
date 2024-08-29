import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from models import *
import sys
import io

from dataformat import *
from config import *


class StreamToTkinter:
    def __init__(self, widget):
        self.widget = widget

    def write(self, message):
        # Append the message to the Tkinter Text widget
        self.widget.insert('end', message)
        self.widget.yview('end')  # Scroll to the end of the widget

    def flush(self):
        # This method is needed for file-like objects but can be left empty
        pass


class PayFlex:

    def __init__(self, root):
        self.file_path = None
        self.root = root
        self.root.title("Payroll Savior")

        # QB file upload section
        self.file_label = tk.Label(root, text="Upload Folder with all Excel and CSV Files:")
        self.file_label.grid(row=0, column=0, padx=5, pady=5, sticky='e')

        self.file_label_button = tk.Button(root, text="Upload", command=self.upload_qb_file)
        self.file_label_button.grid(row=0, column=1, padx=5, pady=5, sticky='w')

        self.file_status = tk.Label(root, text="Current File: None")
        self.file_status.grid(row=0, column=2, padx=5, pady=5, sticky='w')

        # Summary output
        self.summary_button = tk.Button(root, text="Summary", command=self.show_summary)
        self.summary_button.grid(row=5, column=0, padx=5, pady=5, sticky='w')

        self.summary_text = scrolledtext.ScrolledText(root, width=100, height=50)
        self.summary_text.grid(row=6, column=0, columnspan=3, padx=5, pady=5)

    def upload_qb_file(self):
        file_path = filedialog.askdirectory(title="Select Excel Folder")
        if file_path:
            self.file_path = file_path
            self.file_status.config(text=f"Current File: {file_path}")
        else:
            messagebox.showwarning("Warning", "No file selected")

    def get_file_path(self):
        print(self.file_path)
        return self.file_path

    def show_summary(self):
        self.summary_text.delete('1.0', tk.END)

        # Capture printed output
        file_path = self.get_file_path()

        # Redirect stdout to capture the print output
        old_stdout = sys.stdout
        new_stdout = io.StringIO()
        sys.stdout = new_stdout

        try:
            models(file_path)
        finally:
            # Restore original stdout
            sys.stdout = old_stdout

        # Get the captured output
        output = new_stdout.getvalue()

        # Insert new summary text
        if output:
            self.summary_text.insert(tk.END, output)


if __name__ == "__main__":
    root = tk.Tk()
    app = PayFlex(root)
    root.mainloop()
