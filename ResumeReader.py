import re
import os
import logging
import pdfplumber
import sys, fitz


class ResumeReader:

    def convert_docx_to_txt(self, docx_file, docx_parser):
        text = ""
        try:
            clean_text = re.sub(r'\n+', '\n', text)
            # Normalize text blob
            clean_text = clean_text.replace("\r", "\n").replace("\t", " ")
            # Split text blob into individual lines
            resume_lines = clean_text.splitlines()
            # Remove empty strings and whitespaces
            resume_lines = [re.sub('\s+', ' ', line.strip()) for line in resume_lines if
                            line.strip()]
            return resume_lines, text
        except Exception as e:
            logging.error('Error in docx file:: ' + str(e))
            return [], " "

    def convert_pdf_to_txt(self, pdf_file):
        pdf = pdfplumber.open(pdf_file)
        raw_text = ""
        with fitz.open(pdf_file) as doc:
            for page in doc:
                raw_text += page.get_text()
                print(raw_text)
        # for page in pdf.pages:
        #     raw_text += page.extract_text() + "\n"

        pdf.close()                      
        try:
            full_string = re.sub(r'\n+', '\n', raw_text)
            full_string = full_string.replace("\r", "\n")
            full_string = full_string.replace("\t", " ")

            # Remove awkward LaTeX bullet characters
            full_string = re.sub(r"\uf0b7", " ", full_string)
            full_string = re.sub(r"\(cid:\d{0,3}\)", " ", full_string)
            full_string = re.sub(r'• ', " ", full_string)

            # Split text blob into individual lines
            resume_lines = full_string.splitlines(True)

            # Remove empty strings and whitespaces
            resume_lines = [re.sub('\s+', ' ', line.strip()) for line in resume_lines if line.strip()]
           
            return resume_lines, raw_text 
        except Exception as e:
            logging.error('Error in docx file:: ' + str(e))
            return [], " "

    def read_file(self, file,docx_parser = "tika"):
        """
        file : Give path of resume file
        docx_parser : Enter docx2txt or tika, by default is tika
        """
        print("Reading the Resume...")
        # file = "/content/Asst Manager Trust Administration.docx"
        file = os.path.join(file)
        if file.endswith('docx') or file.endswith('doc'):
            # if file.endswith('doc') and docx_parser == "docx2txt":
                # docx_parser = "tika"
                # logging.error("doc format not supported by the docx2txt changing back to tika")
            resume_lines, raw_text = self.convert_docx_to_txt(file, docx_parser)
        elif file.endswith('pdf'):
            resume_lines, raw_text = self.convert_pdf_to_txt(file)
        elif file.endswith('txt'):
            with open(file, 'r', encoding='utf-8') as f:
                resume_lines = f.readlines()

        else:
            resume_lines = None
        
      
        return resume_lines 