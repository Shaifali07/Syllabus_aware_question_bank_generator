from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field

# Load environment variables from .env file
load_dotenv()

# Get the API key
groq_api_key = os.environ.get("GROQ_API_KEY")
llm_topic = ChatGroq(
    model_name="llama-3.1-8b-instant",
    temperature=0)


class Topic_Formation(BaseModel):
    Units: str = Field(description="Unit extracted from the syllabus")
    topics: str = Field(description="Key topics form the unit")


parser_topic = JsonOutputParser(pydantic_object=Topic_Formation)
format_instructions_topic = parser_topic.get_format_instructions()
prompt_topic = ChatPromptTemplate.from_messages([
    ("system", "You are an academic assistant. Your task is to extract structured units from the syllabus."),
    ("human", '''
    Instructions:
    1. Identify all units/modules from the syllabus {syllabus}.
    2. For each unit, extract:
       - unit_name
       - key topics (list of concepts inside the unit)
    3. Clean and organize properly.

    Output format instructions  {format_instructions_topic}

    '''

     )])
chain_topics = prompt_topic | llm_topic | parser_topic
llm=ChatGroq(
    model_name="meta-llama/llama-4-scout-17b-16e-instruct",
    temperature=0)

class Clean_text(BaseModel):
  question: str = Field(description="Question extracted from papers")
  marks: int | None = Field(description="Marks for each question ")
  unit: str | None = Field(description="Unit of each question from syllbus ")
parser_clean_text=JsonOutputParser(pydantic_object=Clean_text)
format_instructions_clean_text = parser_clean_text.get_format_instructions()

prompt_cleaner= ChatPromptTemplate.from_messages ([
    ("system", "You are an expert at processing university exam papers."),
    ("human",'''
    You are given
1. raw extracted text from an exam paper. The text contains noise such as:
headers (university name, subject, date, etc.)
instructions
question numbers (Q.1, Q.2, etc.)
course outcome tags like CO1, CO2
marks like [2], [6]
formatting issues
"OR" sections
mixed sub-questions like (a), (b), (i), (ii)

Your task is to extract clean, meaningful questions.
2. Syllabus units

----------------------
SYLLABUS:
{syllabus}
----------------------
Your tasks:

### Task 1: Clean Questions
Instructions:
Remove all irrelevant text such as:
headers
instructions
page numbers
"Attempt any", "Do as directed", etc.
Extract ONLY actual questions.
keep all sub-questions into the same parent  question:
(a), (b), (c)
(i), (ii), (iii)
numbered lists like 1., 2.
If a question contains multiple logical parts, split them into separate questions.
Remove "OR" and treat alternative questions as independent questions.
Preserve the full meaning of each question.
Extract marks if available, otherwise set marks = null.
Clean formatting:
remove extra spaces
fix broken sentences
### Task 2: Tag Each Question
For each question, assign:
- unit (from syllabus)
Instructions:
- Choose the BEST matching unit
- Do NOT invent new units
- Use only provided syllabus
-topics for each units are {unit_topics} you can use them to decide the unit of the question. You will just return unit and marks for each question not topics.
Output format (STRICT JSON): as per {format_instructions_clean_text}

[
{{
"question": "clean question text",
"marks": number or null
"unit": "unit name",
}}
]

Important:
Do NOT include any explanation.
Do NOT include headers or instructions.
Return ONLY valid JSON.
Ensure each question is complete and readable.

Now process the following text:

{input_text}''')
])
chain=prompt_cleaner | llm|parser_clean_text
def extract_syllabus(syllabus):
    topics = chain_topics.invoke({"syllabus":syllabus,"format_instructions_topic":format_instructions_topic})
    return topics

def Create_question_bank(file_text,unit_names,syllabus):
    result=chain.invoke({"input_text":file_text,"syllabus":unit_names,"unit_topics":syllabus,"format_instructions_clean_text":format_instructions_clean_text})
    return result