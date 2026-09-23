import csv
import os
import json
from datetime import datetime

class ExportHelper:
    @staticmethod
    def export_to_csv(data_dict, file_path="verification_history.csv"):
        """
        Exports a dictionary of verification data to a local CSV file.
        """
        file_exists = os.path.isfile(file_path)
        with open(file_path, mode='a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=list(data_dict.keys()))
            if not file_exists:
                writer.writeheader()
            writer.writerow(data_dict)

    @staticmethod
    def extract_text_ocr(image_path):
        """
        Optional OCR extraction using Tesseract.
        Requires pytesseract and tesseract executable installed.
        """
        try:
            import pytesseract
            from PIL import Image
            return pytesseract.image_to_string(Image.open(image_path))
        except Exception:
            return ""
