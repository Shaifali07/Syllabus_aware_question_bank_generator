import streamlit as st
from pypdf import PdfReader
from llm import extract_syllabus, Create_question_bank
import time
import io
import pandas as pd
st.title("Question Bank Generator 📖")
uploaded_files = st.file_uploader(
    "Upload PDFs of Paper",
    type=["pdf"],
    accept_multiple_files=True
)

text = []


def to_excel(df):
    output = io.BytesIO()
    # Use 'xlsxwriter' as the engine for better performance and formatting options
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    return output.getvalue()
if uploaded_files:
    for file in uploaded_files:
        reader = PdfReader(file)
        file_text = ""

        for page in reader.pages:
            file_text += page.extract_text() or ""

        st.write(f"Read file: {file.name}")
        text.append(file_text)
    # st.write(text)
syllabus = st.text_area("Enter your Syllabus here:",height ="content")
if st.button("Submit"):
    st.write("Processing...")
    units_extracted=extract_syllabus(syllabus)
    unit_names = []
    for t in units_extracted["Units"]:
        unit_names.append(t["unit_name"])
    result = []
    for i, t in enumerate(text):
        file_text = t
        print(f"Processing file {i + 1}...")
        time.sleep(0.2)
        result += Create_question_bank(file_text, unit_names, units_extracted["Units"])
    df = pd.DataFrame(result)
    st.table(df)
    processed_data = to_excel(df)
    st.download_button(
        label="Download Excel File",
        data=processed_data,
        file_name='dataframe_export.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )