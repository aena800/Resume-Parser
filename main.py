#pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-2.3.1/en_core_web_sm-2.3.1.tar.gz

import os
import pandas as pd
import spacy
from resume_parser import resumeparse
import ResumeReader as rr
from ResumeParser import ResumeParser
from Models import Models
from transformers import AutoTokenizer, AutoModelForTokenClassification, AutoModelForSequenceClassification
from transformers import pipeline
from flair.data import Sentence
from flair.models import SequenceTagger
import pickle


spacy.load('en_core_web_sm')


# def parse_cv(file_path):
#     """
#     Parses CVs and returns a DataFrame of parsed data.
#     file_path: The directory containing CV files.
#     n: Number of CVs to parse. By default, it parses 10.
#     """

#     cv_data = resumeparse.read_file(file_path)
#     cv_data.pop("name", None)

#     # added:
#     reader = rr.ResumeReader()
#     cv_text = reader.read_file(file_path)
#     tokenizer = AutoTokenizer.from_pretrained("Jean-Baptiste/camembert-ner-with-dates")
#     model = AutoModelForTokenClassification.from_pretrained("Jean-Baptiste/camembert-ner-with-dates")
#     ner = pipeline('ner', model=model, tokenizer=tokenizer, grouped_entities=True)
#     ner_dates = pipeline('ner', model=model, tokenizer=tokenizer, aggregation_strategy="simple")
#     zero_shot_classifier = pipeline("zero-shot-classification", model='valhalla/distilbart-mnli-12-6')
#     tagger = SequenceTagger.load("flair/pos-english-fast")

#     # Create a ResumeParser object
#     resume_parser = ResumeParser( ner, ner_dates, zero_shot_classifier, tagger)

#     # Parse the resume text
#     resume_parser.parse(cv_text)
#     # added till here , below is the old work:



#     # Extract the skills from the dictionary
#     cand_skills = cv_data.get('skills', [])

#     # Create a new list to store detected languages
#     Languages = []

#     # Iterate through the skills and check if any match a language
#     for skill in cand_skills[:]:  # Using a slice to iterate so we can modify the original list
#         if skill in languages_list:
#             Languages.append(skill)
#             cand_skills.remove(skill)

#     # Update the original dictionary
#     cv_data['skills'] = cand_skills
#     cv_data['languages'] = Languages
#     cleaned_data = {k: v for k, v in cv_data.items() if v}
#     return cleaned_data




def parse_cv(file_path):
    """
    Parses CVs and returns a DataFrame of parsed data.
    file_path: The directory containing CV files.
    n: Number of CVs to parse. By default, it parses 10.
    """

    # Parsing using resume_parser library
    cv_data = resumeparse.read_file(file_path)
    cv_data.pop("name", None)

    # Parsing using your custom ResumeParser
    reader = rr.ResumeReader()
    cv_text = reader.read_file(file_path)
    tokenizer = AutoTokenizer.from_pretrained("Jean-Baptiste/camembert-ner-with-dates")
    model = AutoModelForTokenClassification.from_pretrained("Jean-Baptiste/camembert-ner-with-dates")
    ner = pipeline('ner', model=model, tokenizer=tokenizer, grouped_entities=True)
    ner_dates = pipeline('ner', model=model, tokenizer=tokenizer, aggregation_strategy="simple")
    zero_shot_classifier = pipeline("zero-shot-classification", model='valhalla/distilbart-mnli-12-6')
    tagger = SequenceTagger.load("flair/pos-english-fast")

    # Create a ResumeParser object
    resume_parser_2 = ResumeParser(ner, ner_dates, zero_shot_classifier, tagger)
    # Check if ResumeParser is initialized
    print("Resume Parser Initialized:", isinstance(resume_parser_2, ResumeParser))  # Debug print

    
    # Parse the resume text
    result = resume_parser_2.parse(cv_text)

    print("test: \n" , result)
    #Add new fields from custom_parsed_cv to cv_data
    for key, value in result.items():
        print("key :", key, "value: ", value, "\n")
        cv_data[f"{key}"] = value

   

    # Extract the skills from the combined dictionary
    cand_skills = cv_data.get('skills', [])
    # Sample list of languages
    languages_list = [
        "Afrikaans", "Albanian", "Amharic", "Arabic", "Armenian", "Azerbaijani",
        "Basque", "Belarusian", "Bengali", "Bosnian", "Bulgarian", "Burmese", "Catalan",
        "Cebuano", "Chichewa", "Chinese", "Chinese (Simplified)", "Chinese (Traditional)", "Corsican",
        "Croatian", "Czech", "Danish", "Dutch", "English", "Esperanto", "Estonian",
        "Filipino", "Finnish", "French", "Frisian", "Galician", "Georgian", "German",
        "Greek", "Gujarati", "Haitian Creole", "Hausa", "Hawaiian", "Hebrew", "Hindi",
        "Hmong", "Hungarian", "Icelandic", "Igbo", "Indonesian", "Irish", "Italian",
        "Japanese", "Javanese", "Kannada", "Kazakh", "Khmer", "Korean", "Kurdish (Kurmanj)",
        "Kyrgyz", "Lao", "Latin", "Latvian", "Lithuanian", "Luxembourgish", "Macedonian",
        "Malagasy", "Malay", "Malayalam", "Maltese", "Maori", "Marathi", "Mongolian",
        "Nepali", "Norwegian", "Odia (Oriya)", "Pashto", "Persian", "Polish", "Portuguese",
        "Punjabi", "Romanian", "Russian", "Samoan", "Scots Gaelic", "Serbian", "Sesotho",
        "Shona", "Sindhi", "Sinhala", "Slovak", "Slovenian", "Somali", "Spanish",
        "Sundanese", "Swahili", "Swedish", "Tajik", "Tamil", "Telugu", "Thai", "Turkish",
        "Ukrainian", "Urdu", "Uzbek", "Vietnamese", "Welsh", "Xhosa", "Yiddish", "Yoruba", "Zulu"
    ]
    # Create a new list to store detected languages
    Languages = []

    # Iterate through the skills and check if any match a language
    for skill in cand_skills[:]:
        if skill in languages_list:
            Languages.append(skill)
            cand_skills.remove(skill)

    # Update the combined dictionary
    cv_data['skills'] = cand_skills
    cv_data.pop("skills", None)
    cv_data['languages'] = Languages
    cleaned_data = {k: v for k, v in cv_data.items() if v}
    print("All data: ", cleaned_data)
    return cleaned_data
