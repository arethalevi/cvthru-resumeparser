import io
import re
import spacy
import os
import pandas as pd
import docx2txt

from pdfminer.converter import TextConverter
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from spacy.matcher import Matcher
#from nltk.corpus import stopwords


def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as fh:
        for page in PDFPage.get_pages(fh, caching=True, check_extractable=True):
            resource_manager = PDFResourceManager()
            fake_file_handle = io.StringIO()
            converter = TextConverter(resource_manager,fake_file_handle,codec='utf-8',laparams=LAParams())
            page_interpreter = PDFPageInterpreter(resource_manager,converter)
            page_interpreter.process_page(page)
            text = fake_file_handle.getvalue()
            yield text
            converter.close()
            fake_file_handle.close()

def extract_text_from_doc(doc_path):
    temp = docx2txt.process(doc_path)
    text = [line.replace('\t', ' ') for line in temp.split('\n') if line]
    return ' '.join(text)


nlp = spacy.load('en_core_web_sm')
matcher = Matcher(nlp.vocab)

def extract_name(resume_text):
    nlp_text = nlp(resume_text)
    pattern = [{'POS': 'PROPN'}, {'POS': 'PROPN'}] 
    matcher.add('NAME', [pattern])
    matches = matcher(nlp_text)
    
    for match_id, start, end in matches:
        span = nlp_text[start:end]
        return span.text

def extract_mobile_number(text):
    phone = re.findall(re.compile(r'(?:(?:\+?([1-9]|[0-9][0-9]|[0-9][0-9][0-9])\s*(?:[.-]\s*)?)?(?:\(\s*([2-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9])\s*\)|([0-9][1-9]|[0-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9]))\s*(?:[.-]\s*)?)?([2-9]1[02-9]|[2-9][02-9]1|[2-9][02-9]{2})\s*(?:[.-]\s*)?([0-9]{8})(?:\s*(?:#|x\.?|ext\.?|extension)\s*(\d+))?'), text)
    if phone:
        number = ''.join(phone[0])
        if len(number) > 10:
            return '+' + number
        else:
            return number


def extract_email(email):
    email = re.findall("([^@|\s]+@[^@]+\.[^@|\s]+)", email)
    if email:
        try:
            return email[0].split()[0].strip(';')
        except IndexError:
            return None


def extract_skills(resume_text):
    nlp_text = nlp(resume_text)
    tokens = [token.text for token in nlp_text if not token.is_stop]
    data = pd.read_csv("skills.csv") 
    skills = list(data.columns.values)
    skillset = []
    for token in tokens:
        if token.lower() in skills:
            skillset.append(token)
    for token in nlp_text.noun_chunks:
        token = token.text.lower().strip()
        if token in skills:
            skillset.append(token)
    return [i.capitalize() for i in set([i.lower() for i in skillset])]


def extract_univ(resume_text):
    sub_patterns = ['[A-Z][a-z]* Institute of Technology','[A-Z][a-z]* University','Insitute Technology of [a-zA-Z]+\s[.!?\]*',
                    'University of [A-Z][a-z]*','Universitas [a-zA-Z]+\s[.!?\]',
                    'Ecole [A-Z][a-z]*']
    pattern = '({})'.format('|'.join(sub_patterns))
    matches = re.findall(pattern, resume_text)
    return matches

def extract_degree(resume_text):
    sub_patterns = ['Bachelor of [a-zA-Z\s]+','Master of [a-zA-Z\s]+']
    pattern = '({})'.format('|'.join(sub_patterns))
    matches = re.findall(pattern, resume_text)
    return matches

def extract_gpa(resume_text):
    x=[]
    m = re.findall(r'(\bgpa[ :]+)?(\d+(?:\.\d+)?)[/\d. ]{0,6}(?(1)| *gpa\b)', resume_text, re.I)
    for i in m:
        x.append(i[1])
    return x

def extract_linkedin(s):
    pat = "linkedin"
    pat = r'\b\S*%s\S*\b' % re.escape(pat) 
    return re.findall(pat, s)


def resume_parse_pdf(pdf):
    text = ""
    j = extract_text_from_pdf(pdf)
    for page in j:
        text += ' ' + page
    
    name = extract_name(text)
    phone = extract_mobile_number(text)
    email = extract_email(text)
    education = extract_univ(text)
    degree = extract_degree(text)
    gpa = extract_gpa(text)
    skills = extract_skills(text)
    linkedin = extract_linkedin(text)
    jadi = {
        'name':name,
        'phone':phone,
        'email':email,
        'education':education,
        'degree': degree,
        'gpa':gpa,
        'skills':skills,
        'linkedin':linkedin
    }
    return jadi

def resume_parse_doc(doc):
    text = extract_text_from_doc(doc)
    
    name = extract_name(text)
    phone = extract_mobile_number(text)
    email = extract_email(text)
    education = extract_univ(text)
    degree = extract_degree(text)
    gpa = extract_gpa(text)
    skills = extract_skills(text)
    jadi = {
        'name':name,
        'phone':phone,
        'email':email,
        'education':education,
        'degree': degree,
        'gpa':gpa,
        'skills':skills
    }
    return jadi

def resume_parse(file):
    if os.path.splitext(file)[1] == ".docx":
        s = resume_parse_doc(file)
    elif os.path.splitext(file)[1] == ".pdf" :
        s = resume_parse_pdf(file)
    else:
        s = "invalid"
    return s