from flask import Flask
from flask import render_template, request, redirect
import os
import pandas as pd
import spacy
import resume_parser
from resume_parser import resumeparse
from main import parse_cv


app = Flask(__name__)

UPLOAD_FOLDER = "C:\\Users\\anari\\Documents\\CV-Parser\\cv_app\\cv_samples"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

spacy.load('en_core_web_sm')


@app.route('/', methods=['GET', 'POST'])
def upload_file():
  if request.method == 'POST':
    if 'file' not in request.files:
      return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
      return redirect(request.url)
    if file:
      filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
      file.save(filename)

      # Parse only the uploaded CV
      cv_data = parse_cv(filename)

      return render_template('display_data.html', data=cv_data)
  return render_template('upload.html')


if __name__ == '__main__':
  app.run(debug=True)
