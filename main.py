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
if uploaded_files:
    st.write("Files uploaded!! Please enter the syllabus")
if "text_data" not in st.session_state:
    st.session_state.text_data = []
def to_excel(df):
    output = io.BytesIO()
    # Use 'xlsxwriter' as the engine for better performance and formatting options
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    return output.getvalue()
syllabus = st.text_area("Enter your Syllabus here:",height =400)
if st.button("Submit"):
    with st.spinner("Generating Question Bank..."):

        if not uploaded_files:
            st.warning("Please upload at least one PDF")
            st.stop()

        if not syllabus.strip():
            st.warning("Please enter syllabus")
            st.stop()
        units_extracted = extract_syllabus(syllabus)
        unit_names = []
        for t in units_extracted["Units"]:
            unit_names.append(t["unit_name"])

        result = []
        if uploaded_files:
            for file in uploaded_files:
                reader = PdfReader(file)
                file_text = ""

                for page in reader.pages:
                    file_text += page.extract_text() or ""

                st.write(f"Read file: {file.name}")
                time.sleep(0.2)
                result += Create_question_bank(file_text, unit_names, units_extracted["Units"])


        df = pd.DataFrame(result)
        df["marks"] = pd.to_numeric(df["marks"], errors="coerce")

        df = df.sort_values(
            by=["unit", "marks"],
        )
        df = df.reset_index(drop=True)
        df["Sr No"] = range(1, len(df) + 1)
        df = df[[ "Sr No","unit", "question", "marks"]]
        df.columns = ["Q No","Unit", "Question", "Marks"]
    st.table(df)
    processed_data = to_excel(df)
    st.download_button(
            label="Download Excel File",
            data=processed_data,
            file_name='dataframe_export.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )