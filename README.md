🤖 SmartResume Analyzer

An AI-powered ATS (Applicant Tracking System) resume checker built with Streamlit and Google Gemini. This tool helps job seekers optimize their resumes by evaluating them against job descriptions, identifying missing keywords, and providing actionable improvement suggestions.

✨ Features

ATS Evaluation: Analyzes resumes against job descriptions to provide a percentage match score.
Missing Keywords Identification: Highlights keywords from the job description that are absent in the resume.
Profile Summary Generation: Provides an AI-generated summary of the resume's alignment with the job description.
Improvement Suggestions: Offers specific, actionable advice on how to incorporate missing keywords and enhance resume sections.
Resume Strength Analysis: Visualizes resume strengths across categories like Technical Skills, Soft Skills, Experience, Education, and Projects using a radar chart.
Evaluation History: Maintains a session-based history of analyses, with options to save and load previous results.
Resume Comparison: Allows users to upload multiple resumes and compare their JD match and missing keywords.
PDF Text Extraction: Extracts text efficiently from uploaded PDF resumes.
Interactive UI: User-friendly interface built with Streamlit for a seamless experience.

🚀 Technologies Used

Python
Streamlit: For building the interactive web application.
Google Generative AI (Gemini 2.5 Flash): The Large Language Model (LLM) used for resume analysis, keyword identification, and suggestion generation.
PyPDF2: For extracting text content from PDF files.
Matplotlib: For creating the radar chart visualization.
python-dotenv: For secure management of API keys.
pickle: For saving and loading analysis history.

📸 Screenshots

Main Interface:
A screenshot showing the primary input fields for Job Description and Resume Upload.
Evaluation Results:
A screenshot displaying the JD Match score, Missing Keywords, Profile Summary, and Improvement Suggestions.
Radar Chart Analysis:
A screenshot of the radar chart visualizing resume strengths.
⚙️ How to Run Locally
Follow these steps to set up and run the SmartResume Analyzer on your local machine.
1. Prerequisites
Python 3.8+: Ensure you have Python installed.
Google Gemini API Key: Obtain an API key from Google AI Studio.
2. Clone the Repository
git clone https://github.com/Vanshika300/smart-resume-analyzer.git
cd smart-resume-analyzer


3. Configure API Key
Create a file named .env in the root directory of your project (the same directory as resume_analyzer.py). Add your Google Gemini API key to it:
GOOGLE_API_KEY="YOUR_ACTUAL_GOOGLE_GEMINI_API_KEY"


Important: Replace "YOUR_ACTUAL_GOOGLE_GEMINI_API_KEY" with your real key. This file is ignored by Git and will not be uploaded to GitHub, keeping your key secure.
4. Install Dependencies
It's highly recommended to use a virtual environment:
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows:
.\venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install required Python packages
pip install -r requirements.txt


5. Run the Application
Once all dependencies are installed and your .env file is configured, run the Streamlit application from your terminal:
streamlit run resume_analyzer.py


This command will open the application in your web browser, usually at http://localhost:8501.
📧 Contact
Feel free to reach out if you have any questions or feedback!
Email: vanshikashukla065@gmail.com
LinkedIn: linkedin.com/in/vanshika-shukla30
