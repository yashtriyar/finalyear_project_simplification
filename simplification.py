import streamlit as st
import pathlib
import textwrap
from langchain_google_genai import ChatGoogleGenerativeAI
import os
import docx
import fitz  
from comtypes import client
import google.generativeai as genai
from IPython.display import display
from IPython.display import Markdown


# def to_markdown(text):
#   text = text.replace('•', '*')
#   return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))



# --- Document Extraction Functions ---
def extract_text_from_docx(docx_path):
    doc = docx.Document(docx_path)
    text = []
    for paragraph in doc.paragraphs:
        text.append(paragraph.text)
    return '\n'.join(text)
 

def extract_text_from_pdf(pdf_path):
    text = []
    with fitz.open(pdf_path) as pdf_document:
        for page_number in range(pdf_document.page_count):
            page = pdf_document[page_number]
            text.append(page.get_text())
    return '\n'.join(text)
  

def extract_text_from_doc(doc_path):
    word = client.CreateObject('Word.Application')
    doc = word.Documents.Open(doc_path)
    text = doc.Range().Text
    doc.Close()
    word.Quit()
    return text

def extract_text_from_document(document_path):
    _, file_extension = os.path.splitext(document_path)
    if file_extension.lower() == '.docx':
        return extract_text_from_docx(document_path)
    elif file_extension.lower() == '.pdf':
        return extract_text_from_pdf(document_path)
    elif file_extension.lower() == '.doc':
        return extract_text_from_doc(document_path)
    else:
        raise ValueError(f"Unsupported file format: {file_extension}")
st.title("Document Summarizer and Analyzer")

# Secure API key input (consider using Streamlit secrets)
api_key = st.text_input("Enter your Google Gemini API Key", type="password")
GOOGLE_API_KEY=api_key
llm = ChatGoogleGenerativeAI(model="gemini-pro",google_api_key=api_key)
# model = genai.GenerativeModel('gemini-pro')

uploaded_file = st.file_uploader("Choose a document (.docx, .pdf, .doc)", type=["docx", "pdf", "doc"])

if uploaded_file is not None:
  file_path = pathlib.Path(uploaded_file.name)
  with open(file_path, 'wb') as f:
    f.write(uploaded_file.getvalue()) 

  try:
    extracted_text = extract_text_from_document(file_path)
    with st.sidebar:
        st.subheader("Original Text")
        st.write(extracted_text) 
    prompt1=f'''Read the content -{extracted_text}. 
    As a geniune helpfull assistance, generate about 10 to 20 queries based on the content. As these contents are an extract of a legal document, make sure the queries are also legal based. You can also ask queries around any potential pitfalls or attempts at deception related to the usage of service to help users avoid any misunderstandings or misuse. Spot out any traps and loophole in the terms and conditions which can in future harm the person. point out those scenarios.


    '''
    prompt2=f'''generate the answers of {prompt1} on the basis of {extracted_text} undermining the legal terms and document. explain the answers in layman terms insuring that the user understands the legal scenarios as well


    '''

    prompt = f'''You are a helpful assistant that gives a long summary of the {extracted_text} in layman language and shows output in bulletin format.
    Also combine the {prompt1} with their corresponding answers of {prompt2}
    prompt is 
    Tone conversational ,spartan, useless corporate jargon
    ''' 
    #response = llm.generate_content(prompt)
    st.subheader("Summary and Analysis")
    result = llm.invoke(prompt)
    st.write(result.content)
    # generated_text = response.candidates[0]['content']['parts'][0]['text'] 
    # generated_response = response.result['candidates'][0]['content']['parts'][0]['text']
    # st.write(generated_text) 
 

  except Exception as e:
    st.error(f"Error processing file: {e}")
