import os
import pandas as pd
import re
from flask import current_app

class EmailNotFound(Exception):
    pass

class FileExtensionError(Exception):
    pass

def get_file_extension(file_name):
    root, extension = os.path.splitext(file_name)
    return extension

def read_file(file_name):
    file_ext = get_file_extension(file_name)
    path = os.path.join(current_app.root_path, 'static/files', file_name)
    if file_ext:
        if file_ext == '.csv':
            try:   
                file = pd.read_csv(fr"{path}")
                return file
            except Exception as e:
                raise Exception(e)
        elif file_ext == '.xlsx':
            try:
                file = pd.read_excel(fr"{path}")
                return file
            except Exception as e:
                raise Exception(e)
    else:
        raise FileExtensionError("Uploaded file extension is not recognised, make sure you upload .csv or .xlsx format only")
            
class UploadContact:
    """Check if file is readable, has email in data"""
    def __init__(self, file_name):
        self.file_name = file_name
        self.df = read_file(file_name=file_name)
    
    def check_if_file_has_email(self):
        """Check all values of first five rows to find if it has email"""
        for col in self.df.columns:
            col_head = self.df[col].head()
            for data in col_head:
                email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
                if re.match(email_regex, str(data)) is not None:
                    return True
        raise EmailNotFound("""EmailNotFound: First five rows of the file does not have any cell containing email""")

class MapContacts:
    def __init__(self, filename):
        self.filename = filename
        self.df = read_file(file_name=filename)
        self.data = {}
        self.columns_with_email = []

    def detect_columns_containing_email(self):
        for col in self.df.columns:
            col_head = self.df[col].head()
            for data in col_head:
                email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
                if re.match(email_regex, str(data)) is not None:
                    self.columns_with_email.append(col)

    def analyze_file(self):
        self.detect_columns_containing_email()
        total_rows = len(self.df)
        self.data["columns"] = self.df.columns.tolist()
        self.data["total_columns"] = len(self.df.columns)
        self.data["total_rows"] = total_rows
        self.data["columns_with_email"] = self.columns_with_email
        return self.data
    
    def delete_file(self):
        """This function will be called after upload is successful to delete the file"""
        path = os.path.join(current_app.root_path, 'static/files', self.filename)
        os.remove(path)
        print("**************** FILE DELETED")