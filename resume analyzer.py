import streamlit as st
import google.generativeai as genai
import os
import PyPDF2 as pdf

import json
import re
from datetime import datetime
import base64
import time
import matplotlib.pyplot as plt
import pickle


# Configure the Gemini API with the API key

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
#Set API Key for Gemini model
genai.configure(api_key=GOOGLE_API_KEY)

def get_gemini_response(input):
    """
    Generate a response using the Gemini AI model.

    Args:
    input (str): The input prompt for the AI model.

    Returns:
    str: The generated response text.
    """
    model = genai.GenerativeModel('gemini-2.5-flash')
    with st.spinner("Analyzing..."):
        # Simulate progress with a progress bar
        progress_bar = st.progress(0)
        for i in range(100):
            time.sleep(0.01)  # Reduced sleep time for faster response
            progress_bar.progress(i + 1)
        response = model.generate_content(input)
    return response.text


def input_pdf_text(uploaded_file):
    """
    Extract text from an uploaded PDF file.

    Args:
    uploaded_file (UploadedFile): The uploaded PDF file.

    Returns:
    str: Extracted text from the PDF, or None if an error occurs.
    """
    try:
        reader = pdf.PdfReader(uploaded_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        st.error(f"Error reading PDF: {str(e)}")
        return None


def parse_ai_response(response):
    """
    Parse the AI response into a JSON object.

    Args:
    response (str): The raw response from the AI.

    Returns:
    dict: Parsed JSON object, or None if parsing fails.
    """
    response = response.strip()
    if response.startswith('{') and response.endswith('}'):
        try:
            parsed = json.loads(response)
            # Convert percentage strings to floats
            for key in ['JD Match', 'TechnicalSkills', 'SoftSkills', 'Experience', 'Education', 'Projects']:
                if key in parsed and isinstance(parsed[key], str):
                    parsed[key] = float(parsed[key].rstrip('%'))
            return parsed
        except json.JSONDecodeError as e:
            st.error(f"JSON parsing error: {str(e)}")
            return None
    else:
        # Try to extract JSON from the response if it's not a complete JSON string
        match = re.search(r'\{.*\}', response, re.DOTALL)
        if match:
            try:
                parsed = json.loads(match.group())
                # Convert percentage strings to floats
                for key in ['JD Match', 'TechnicalSkills', 'SoftSkills', 'Experience', 'Education', 'Projects']:
                    if key in parsed and isinstance(parsed[key], str):
                        parsed[key] = float(parsed[key].rstrip('%'))
                return parsed
            except json.JSONDecodeError as e:
                st.error(f"JSON parsing error in extracted content: {str(e)}")
                return None
    st.error("Could not find valid JSON in the response")
    return None


def get_download_link(text):
    """
    Generate a download link for the given text.

    Args:
    text (str): The text to be downloaded.

    Returns:
    str: HTML string containing the download link.
    """
    b64 = base64.b64encode(text.encode()).decode()
    return f'<a href="data:file/txt;base64,{b64}" download="evaluation_history.txt">Download Evaluation History</a>'


def suggest_improvements(missing_keywords, job_description):
    """
    Generate improvement suggestions based on missing keywords and job description.

    Args:
    missing_keywords (list): List of missing keywords.
    job_description (str): The job description.

    Returns:
    str: Suggestions for improvement.
    """
    prompt = f"""
    Given the following missing keywords from a resume and the job description, 
    provide specific suggestions on how to incorporate these keywords into the resume effectively. 
    Consider the context of the job description when making suggestions.

    Missing Keywords: {', '.join(missing_keywords)}

    Job Description:
    {job_description}

    Please provide detailed suggestions for each keyword, including:
    1. Where in the resume to add the keyword (e.g., skills section, work experience, etc.)
    2. How to phrase it naturally within the context of the resume
    3. If applicable, suggest a brief example of how to demonstrate experience with the keyword

    Format your response as a bulleted list for easy reading.
    """
    suggestions = get_gemini_response(prompt)
    return suggestions


def create_radar_chart(parsed_response):
    """
    Create a radar chart to visualize resume strengths.

    Args:
    parsed_response (dict): Parsed AI response containing scores.

    Returns:
    matplotlib.figure.Figure: The created radar chart.
    """
    categories = ['Technical Skills', 'Soft Skills', 'Experience', 'Education', 'Projects']
    scores = []
    for category in categories:
        try:
            score = float(parsed_response.get(category.replace(' ', ''), 0))
            scores.append(score)
        except ValueError:
            st.warning(f"Invalid score for {category}. Using 0.")
            scores.append(0)

    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(projection='polar'))
    ax.plot(categories, scores)
    ax.fill(categories, scores, alpha=0.25)
    plt.title('Resume Strength Analysis')
    return fig


def save_analysis(filename, data):
    """
    Save analysis data to a file.

    Args:
    filename (str): Name of the file to save data to.
    data (object): Data to be saved.
    """
    with open(filename, 'wb') as f:
        pickle.dump(data, f)


def load_analysis(filename):
    """
    Load analysis data from a file.

    Args:
    filename (str): Name of the file to load data from.

    Returns:
    object: Loaded data.
    """
    with open(filename, 'rb') as f:
        return pickle.load(f)


# Define the input prompt for the AI model
input_prompt = """
Hey Act Like a skilled or very experienced ATS (Application Tracking System)
with a deep understanding of tech field, software engineering, data science, data analyst
and big data engineer. Your task is to evaluate the resume based on the given job description.
You must consider the job market is very competitive and you should provide 
best assistance for improving the resumes. Assign the percentage Matching based 
on JD and the missing keywords with high accuracy
resume: {text}
description: {jd}

I want the response in a valid JSON string having the structure
{{"JD Match": "% (as a string)", "MissingKeywords": ["keyword1", "keyword2", ...], "Profile Summary": "summary text",
"TechnicalSkills": "score", "SoftSkills": "score", "Experience": "score", "Education": "score", "Projects": "score"}}

IMPORTANT: Ensure your response is a valid JSON string. Do not include any additional text outside the JSON structure.
"""

# Initialize session state for history
if 'history' not in st.session_state:
    st.session_state.history = []

# Streamlit app setup
st.set_page_config(page_title="SmartResume Analyzer")
st.title("SmartResume Analyzer")
st.text("AI-Powered ATS Resume Checker: Optimize Your Resume for Job Success")

# Sidebar
st.sidebar.title("Evaluation History")


# Function to display evaluation history
def display_evaluation_history():
    if len(st.session_state.history) == 0:
        st.sidebar.write("No evaluations yet.")
    else:
        for i, item in enumerate(st.session_state.history):
            with st.sidebar.expander(f"Evaluation {i + 1} - {item['date']}"):
                st.write(f"JD Match: {item['match']}")
                st.write("Missing Keywords:")
                st.write(", ".join(item['keywords']))

        # Generate downloadable history
        history_text = ""
        for i, item in enumerate(st.session_state.history):
            history_text += f"Evaluation {i + 1} - {item['date']}\n"
            history_text += f"JD Match: {item['match']}\n"
            history_text += f"Missing Keywords: {', '.join(item['keywords'])}\n\n"

        st.sidebar.markdown(get_download_link(history_text), unsafe_allow_html=True)


# Display initial evaluation history
display_evaluation_history()

# Save and Load Analysis functionality (in sidebar)
st.sidebar.title("Save/Load Analysis")
if st.sidebar.button("Save Analysis"):
    save_analysis("resume_analysis.pkl", st.session_state.history)
    st.sidebar.success("Analysis saved successfully!")

if st.sidebar.button("Load Previous Analysis"):
    try:
        loaded_history = load_analysis("resume_analysis.pkl")
        st.session_state.history = loaded_history
        st.sidebar.success("Previous analysis loaded successfully!")
        # Update the displayed history
        display_evaluation_history()
    except FileNotFoundError:
        st.sidebar.error("No saved analysis found.")

# Resume comparison feature
st.sidebar.title("Compare Resumes")
compare_mode = st.sidebar.checkbox("Enable Resume Comparison")

# Main app interface
jd = st.text_area("Paste the Job Description")
uploaded_file = st.file_uploader("Upload Your Resume", type="pdf", help="Please upload the pdf")

submit = st.button("Submit")

if submit:
    if uploaded_file is not None:
        if uploaded_file.type == "application/pdf":
            with st.spinner("Analyzing your resume..."):
                # Extract text from the uploaded PDF
                text = input_pdf_text(uploaded_file)
                if text:
                    # Generate AI response based on the resume and job description
                    response = get_gemini_response(input_prompt.format(text=text, jd=jd))
                    parsed_response = parse_ai_response(response)

                    if parsed_response:
                        st.subheader("ATS Evaluation Results")

                        # Display JD Match and Missing Keywords
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("JD Match", f"{parsed_response['JD Match']:.1f}%")
                        with col2:
                            st.subheader("Missing Keywords")
                            if parsed_response["MissingKeywords"]:
                                st.write(", ".join(parsed_response["MissingKeywords"]))
                            else:
                                st.write("No missing keywords found.")

                        # Display Profile Summary
                        st.subheader("Profile Summary")
                        st.write(parsed_response["Profile Summary"])

                        # Display suggestions to add missing keywords
                        st.subheader("Suggestions to Add Missing Keywords")
                        if parsed_response["MissingKeywords"]:
                            suggestions = suggest_improvements(parsed_response["MissingKeywords"], jd)
                            st.write(suggestions)
                        else:
                            st.write("No suggestions needed. Your resume already includes all relevant keywords.")

                        # Display resume strength analysis chart
                        st.subheader("Resume Strength Analysis")
                        fig = create_radar_chart(parsed_response)
                        st.pyplot(fig)

                        # Add current analysis to history
                        st.session_state.history.append({
                            'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            'match': f"{parsed_response['JD Match']:.1f}%",
                            'keywords': parsed_response["MissingKeywords"],
                        })

                        # Update the displayed history in real-time
                        display_evaluation_history()
                    else:
                        st.error("Failed to parse the AI response. Please check the debugging information for details.")
        else:
            st.error("Please upload a PDF file.")
    else:
        st.warning("Please upload a PDF resume to proceed.")

if compare_mode:
    uploaded_files = st.file_uploader("Upload Resumes for Comparison", type="pdf", accept_multiple_files=True)
    if uploaded_files:
        comparison_results = []
        for file in uploaded_files:
            text = input_pdf_text(file)
            if text:
                response = get_gemini_response(input_prompt.format(text=text, jd=jd))
                parsed_response = parse_ai_response(response)
                if parsed_response:
                    comparison_results.append({
                        "filename": file.name,
                        "match": f"{parsed_response['JD Match']:.1f}%",
                        "missing_keywords": parsed_response["MissingKeywords"]
                    })

        st.subheader("Resume Comparison Results")
        for result in comparison_results:
            with st.expander(result["filename"]):
                st.write(f"JD Match: {result['match']}")
                st.write("Missing Keywords:", ", ".join(result["missing_keywords"]))

# Debugging section
if st.checkbox("Show debugging information"):
    st.subheader("Debugging Information")
    st.write("API Key status:", "Set" if os.getenv("GOOGLE_API_KEY") else "Not set")
    st.write("Job Description length:", len(jd))
    if uploaded_file:
        st.write("Uploaded file name:", uploaded_file.name)
        st.write("Uploaded file size:", uploaded_file.size, "bytes")
    if 'response' in locals():
        st.subheader("Raw AI Response")
        st.code(response, language="json")
        st.subheader("Parsed Response")
        st.json(parsed_response)
    st.subheader("Session State History")
    st.json(st.session_state.history)