from Models import Models
from ResumeSegmenter import ResumeSegmenter
from datetime import datetime
from dateutil import parser
import re
from string import punctuation
from flair.data import Sentence

class ResumeParser:
    def __init__(self, ner, ner_dates, zero_shot_classifier, tagger):
        self.models = Models()
        self.segmenter = ResumeSegmenter(zero_shot_classifier)
        self.ner, self.ner_dates, self.zero_shot_classifier, self.tagger = ner, ner_dates, zero_shot_classifier, tagger 
        self.parsed_cv = {}

    # def parse(self, resume_lines):
    #     resume_segments = self.segmenter.segment(resume_lines)
    #     print("***************************** Parsing the Resume...***************************** ")
    #     for segment_name in resume_segments:
    #         if segment_name == "work_and_employment":
    #             resume_segment = resume_segments[segment_name]
    #             print("\nParsing Job history:\n")
    #             print(self.parse_job_history(resume_segment))
                
    #         elif segment_name == "contact_info":
    #             contact_info = resume_segments[segment_name]
    #             print("\nParsing contact info:\n")
    #             print(self.parse_contact_info(contact_info))
                
    #         elif segment_name == "education_and_training":
    #             education_and_training = resume_segments[segment_name]
    #             print("\nParsing education:\n")
    #             print(self.parse_education(education_and_training))
                
    #         elif segment_name == "skills_header":
    #             skills_header = resume_segments[segment_name]
    #             self.parse_skills(skills_header)
    #             print("\nParsing skills:\n", resume_segment)
    #         #     print("************************************** SKILLS HEADER ***************************** <br>",skills_header)
    #     return self.parsed_cv

    def parse(self, resume_lines):
        resume_segments = self.segmenter.segment(resume_lines)
        print("***************************** Parsing the Resume...***************************** ")

        print("Checking if the segments are populated correctly\n")
        print("\nResume Segments:\n")
        for segment_name, segment_data in resume_segments.items():
            print(f"\n{segment_name}:\n")
            print(segment_data)

        for segment_name in resume_segments:
            print ("Name of the segment about to get segmented:\n " , segment_name,"\n")
            if segment_name == "work_and_employment":
                resume_segment = resume_segments[segment_name]
                print("\nParsing Job history:\n")
                job_res = self.parse_job_history(resume_segment)
                print("JOB HISTORY RESULTS : " , job_res, "\n")

            elif segment_name == "contact_info":
                contact_info = resume_segments[segment_name]
                print("\nParsing contact info:\n")
                self.parse_contact_info(contact_info)
                
            elif segment_name == "education_and_training":
                education_and_training = resume_segments[segment_name]
                print("\nParsing education:\n")
                self.parse_education(education_and_training)           

            elif segment_name =='objective':
                obj = resume_segments[segment_name]
                self.parse_objectives(obj)

            elif segment_name == "skills":
                skills_header = resume_segments[segment_name]
                print("\nParsing skills:\n")
                self.parse_skills(skills_header)
                self.extract_contact_info_from_skills()
                  # Corrected from resume_segment to skills_header
        return self.parsed_cv
    

    def parse_education(self, education_and_training):
        edu = self.find_education_info(education_and_training)
        #print(education_and_training)
        self.parsed_cv['Education'] = edu
        return edu
        
    def parse_skills(self, skills):
        skills_list = []
        for line in skills:
            # Split by common delimiters
            for delimiter in [',', ';', '\n']:
                line = line.replace(delimiter, ' ')
            # Split by space and clean up the results
            skills_list.extend([skill.strip() for skill in line.split() if skill.strip()])
        return skills_list


    def parse_objectives(self, objective):
        objectives = []
        for line in objective:
            objectives.extend(line.split(', '))
        return objectives


    def parse_contact_info(self, contact_info):
        contact_info_dict = {}
        name = self.find_person_name(contact_info)
        #email = self.find_contact_email(contact_info)
        self.parsed_cv['Name'] = name
        #contact_info_dict["Email"] = email
        self.parsed_cv['Contact Info'] = contact_info_dict
        return name, contact_info_dict
    
    def extract_contact_info_from_skills(self):
        # Extract contact info from skills and move it to Contact Info
        skills = self.parsed_cv.get('Skills', [])
        contact_info = []
        for skill in skills:
            if any(keyword in skill.lower() for keyword in ["email", "phone", "address"]):
                contact_info.append(skill)
                skills.remove(skill)
        self.parsed_cv['Skills'] = skills
        self.parsed_cv['Contact Info'] = contact_info

    def find_person_name(self, items):
        class_score = []
        splitter = re.compile(r'[{}]+'.format(re.escape(punctuation.replace("&", "") )))
        classes = ["person name", "address", "email", "title"]
        for item in items: 
            elements = splitter.split(item)
            for element in elements:
                element = ''.join(i for i in element.strip() if not i.isdigit())
                if not len(element.strip().split()) > 1: continue
                out = self.zero_shot_classifier(element, classes)
                highest = sorted(zip(out["labels"], out["scores"]), key=lambda x: x[1])[-1]
                if highest[0] == "person name":
                    class_score.append((element, highest[1]))
        if len(class_score):
            return sorted(class_score, key=lambda x: x[1], reverse=True)[0][0]
        return ""
    
    def find_education_info(self, education_and_training):
        education_info = []
        classes = ["institution", "degree", "date", "field of study"]

        for line in education_and_training:
            education_entry = {}
            
            # Additional logic to identify education lines
            if any(keyword in line.lower() for keyword in ["university", "college", "school", "bachelor", "master", "phd", "bs", "ms", "mba"]):
                education_entry["Education"] = line
                education_info.append(education_entry)
                continue  # Skip to the next line since we've identified this as an education line

            # Original logic using zero-shot classifier
            out = self.zero_shot_classifier(line, classes)
            class_score = zip(out["labels"], out["scores"])
            highest = sorted(class_score, key=lambda x: x[1])[-1]

            # Extracting institution name
            if highest[0] == "institution":
                education_entry["Institution"] = line

            # Extracting degree and field of study
            elif highest[0] == "degree" or highest[0] == "field of study":
                education_entry["Degree"] = line

            # Extracting dates
            elif highest[0] == "date":
                dates = self.get_ner_in_line(line, "DATE")
                if dates:
                    education_entry["Dates"] = dates

            if education_entry:
                education_info.append(education_entry)
        print ("Extracted Education INfo: ", education_info)
        return education_info



    def parse_job_history(self, resume_segment):
        idx_job_title = self.get_job_titles(resume_segment)
        print("Fetched indices of Job titles:", idx_job_title, "\n")
        
        # If no job titles are found, return the entire segment
        if not idx_job_title:
            self.parsed_cv["Job History"] = resume_segment
            return resume_segment
        
        current_and_below = False
        if idx_job_title[0][0] == 0:
            current_and_below = True
        
        job_history = []
        for ls_idx, (idx, job_title) in enumerate(idx_job_title):
            job_info = {}
            job_info["Job Title"] = self.filter_job_title(job_title)
            
            if current_and_below:
                line1, line2 = idx, idx + 1
            else:
                line1, line2 = idx, idx - 1
            
            job_info["Company"] = self.get_job_company(line1, line2, resume_segment)
            
            if current_and_below:
                st_span = idx
            else:
                st_span = idx - 1
            
            if ls_idx == len(idx_job_title) - 1:
                end_span = len(resume_segment)
            else:
                end_span = idx_job_title[ls_idx + 1][0]
            
            start, end = self.get_job_dates(st_span, end_span, resume_segment)
            job_info["Start Date"] = start
            job_info["End Date"] = end
            
            print("Job Info:", job_info)
            job_history.append(job_info)
        
        print("Job History:", job_history)
        self.parsed_cv["Job History"] = job_history
        return self.parsed_cv["Job History"]

    # def get_job_titles(self, resume_segment):
    #     classes = ["organization", "institution", "company", "job title", "work details"]
    #     idx_line = []
    #     for idx, line in enumerate(resume_segment):
    #         line_modifed = ''.join(i for i in line if not i.isdigit())
    #         sentence = self.models.get_flair_sentence(line_modifed)
    #         self.tagger.predict(sentence)
    #         tags = [entity.tag for entity in sentence.get_spans('pos')]
            
    #         # Check if tags list is empty
    #         if not tags:
    #             print("No tags for line:", line)
    #             continue
            
    #         # Check if most common tag is a noun
    #         most_common_tag = max(set(tags), key=tags.count)
    #         is_noun = most_common_tag in ["NNP", "NN"]

    #         # Check zero-shot classifier output
    #         out = self.zero_shot_classifier(line, classes)
    #         class_score = zip(out["labels"], out["scores"])
    #         highest = sorted(class_score, key=lambda x: x[1])[-1]
    #         is_job_title_or_org = highest[0] in ["job title", "organization"]

    #         # Print debugging information
    #         print("Line:", line)
    #         print("Tags:", tags)
    #         print("Most Common Tag:", most_common_tag)
    #         print("Is Noun:", is_noun)
    #         print("Zero-shot output:", out)
    #         print("Highest score:", highest)
    #         print("Is Job Title or Org:", is_job_title_or_org)
    #         print("--------")
    def get_job_titles(self, resume_segment):
        classes = ["organization", "institution", "company", "job title", "work details"]
        idx_line = []
        for idx, line in enumerate(resume_segment):
            has_verb = False
            line_modifed = ''.join(i for i in line if not i.isdigit())
            sentence = Sentence(line_modifed)
            self.tagger.predict(sentence)
            tags = []
            for entity in sentence.get_spans('pos'):
                tags.append(entity.tag)
                if entity.tag.startswith("V"): 
                    has_verb = True
            if tags:
                most_common_tag = max(set(tags), key=tags.count)
                is_noun = most_common_tag in ["NNP", "NN"]
                out = self.zero_shot_classifier(line, classes)
                class_score = zip(out["labels"], out["scores"])
                highest = sorted(class_score, key=lambda x: x[1])[-1]
                is_job_title_or_org = highest[0] in ["job title", "organization"]
                print("Line:", line)
                print("Tags:", tags)
                print("Most Common Tag:", most_common_tag)
                print("Is Noun:", is_noun)
                print("Zero-shot output:", out)
                print("Highest score:", highest)
                print("Is Job Title or Org:", is_job_title_or_org)
                print("--------")
                if is_noun and not has_verb and is_job_title_or_org:
                    idx_line.append((idx, line))
            else:
                print("No tags for line:", line)
                    
        print("Job Title indices:", idx_line, "\n")
        return idx_line


    def get_job_dates(self, st, end, resume_segment):
        search_span = resume_segment[st:end]
        dates = []
        for line in search_span:
            for dt in self.get_ner_in_line(line, "DATE"):
                if self.isvalidyear(dt.strip()):
                    dates.append(dt)
        if len(dates): first = dates[0]
        exists_second = False
        if len(dates) > 1:
            exists_second = True
            second = dates[1]
        if len(dates) > 0:
            if self.has_two_dates(first):
                d1, d2 = self.get_two_dates(first)
                print ("Job dates: " , self.format_date(d1), self.format_date(d2))
                return self.format_date(d1), self.format_date(d2)
            elif exists_second and self.has_two_dates(second): 
                d1, d2 = self.get_two_dates(second)
                print ("Job dates: " , self.format_date(d1), self.format_date(d2))
                return self.format_date(d1), self.format_date(d2)
            else:
                if exists_second: 
                    st = self.format_date(first)
                    end = self.format_date(second)
                    print ("start adn end date: ", st, end, "\n")
                    return st, end
                else:
                    print ("job dates: ", self.format_date(first), "", "\n")
                    return (self.format_date(first), "") 
        else: return ("", "")

    def filter_job_title(self, job_title):
        job_title_splitter = re.compile(r'[{}]+'.format(re.escape(punctuation.replace("&", "") )))
        job_title = ''.join(i for i in job_title if not i.isdigit())
        tokens = job_title_splitter.split(job_title)
        tokens = [''.join([i for i in tok.strip() if (i.isalpha() or i.strip()=="")]) for tok in tokens if tok.strip()] 
        classes = ["company", "organization", "institution", "job title", "responsibility",  "details"]
        new_title = []
        for token in tokens:
            if not token: continue
            res = self.zero_shot_classifier(token, classes)
            class_score = zip(res["labels"], res["scores"])
            highest = sorted(class_score, key=lambda x: x[1])[-1]
            if (highest[0] == "job title") or (highest[0] == "organization"):
            # if highest[0] == "job title":
                new_title.append(token.strip())
        if len(new_title):
            return ', '.join(new_title)
        else: return ', '.join(tokens)

    def has_two_dates(self, date):
        years = self.get_valid_years()
        count = 0
        for year in years:
            if year in str(date):
                count+=1
        return count == 2

    def get_two_dates(self, date):
        years = self.get_valid_years()
        idxs = []
        for year in years:
            if year in date: 
                idxs.append(date.index(year))
        min_idx = min(idxs)  
        first = date[:min_idx+4]
        second = date[min_idx+4:]
        return first, second

    def get_valid_years(self):
        current_year = datetime.today().year
        years = [str(i) for i in range(current_year-100, current_year)]
        return years

    def format_date(self, date):
        out = self.parse_date(date)
        if out: 
            return out
        else: 
            date = self.clean_date(date)
            out = self.parse_date(date)
            if out: 
                return out
            else: 
                return date

    def clean_date(self, date): 
        try:
            date = ''.join(i for i in date if i.isalnum() or i =='-' or i == '/')
            return date
        except:
            return date

    def parse_date(self, date):
        try:
            date = parser.parse(date)
            return date.strftime("%m-%Y")
        except:
            try:
                date = datetime(date)
                return date.strftime("%m-%Y")
            except:
                return 0

    def isvalidyear(self, date):
        current_year = datetime.today().year
        years = [str(i) for i in range(current_year-100, current_year)]
        for year in years:
            if year in str(date):
                return True 
        return False

    def get_ner_in_line(self, line, entity_type):
        if entity_type == "DATE": ner = self.ner_dates
        else: ner = self.ner
        return [i['word'] for i in ner(line) if i['entity_group'] == entity_type]     

    def get_job_company(self, idx, idx1, resume_segment):
        job_title = resume_segment[idx]
        if not idx1 <= len(resume_segment)-1: context = ""
        else:context = resume_segment[idx1]
        candidate_companies = self.get_ner_in_line(job_title, "ORG") + self.get_ner_in_line(context, "ORG")
        classes = ["organization", "company", "institution", "not organization", "not company", "not institution"]
        scores = []
        for comp in candidate_companies:
            res = self.zero_shot_classifier(comp, classes)['scores']
            scores.append(max(res[:3]))
        sorted_cmps = sorted(zip(candidate_companies, scores), key=lambda x: x[1], reverse=True)
        if len(sorted_cmps): return sorted_cmps[0][0]
        return context
