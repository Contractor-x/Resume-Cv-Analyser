import os
import streamlit as st
import requests
import json
from dotenv import load_dotenv
import PyPDF2
import io

# Load environment variables
load_dotenv()

# Set up the API key
PERPLEXITY_API_KEY = os.getenv("ppk-MqtLtl0KZ9SzscJmX1Bo7Sc2lW709KckviGPFn2RzOaYBlan")
if not PERPLEXITY_API_KEY:
    PERPLEXITY_API_KEY = st.secrets.get("PERPLEXITY_API_KEY", "")

def extract_text_from_pdf(pdf_file):
    """Extract text from uploaded PDF file"""
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_file.read()))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        st.error(f"Error extracting text from PDF: {e}")
        return ""

def analyze_resume(resume_text, job_description):
    """Analyze resume against job description using Perplexity Sonar API"""
    
    # Ensure API key is available
    if not PERPLEXITY_API_KEY:
        st.error("Perplexity API key not found. Please set up your API key.")
        return None
    
    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json"
    }
    
    prompt = f"""
    You are a professional resume reviewer and job application expert. 
    
    Job Description:
    {job_description}
    
    Resume:
    {resume_text}
    
    Analyze the resume against the job description and provide:
    
    1. Keyword Match Analysis: Identify keywords from the job description and check if they appear in the resume.
    2. Missing Skills: List important skills mentioned in the job description that are missing in the resume.
    3. Skills Alignment: Rate how well the candidate's skills align with the job requirements (score out of 10).
    4. Experience Relevance: Determine if the candidate's experience is relevant to the position.
    5. Specific Improvement Suggestions: Provide actionable suggestions for improving the resume.
    6. ATS Optimization: Suggest how to optimize the resume for Applicant Tracking Systems.
    
    Format your response as clear sections with bullet points for easy readability.
    """
    
    data = {
        "model": "sonar-small-online",
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }
    
    try:
        response = requests.post(
            "https://api.perplexity.ai/chat/completions",
            headers=headers,
            json=data
        )
        
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            st.error(f"Error from API: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error(f"Error calling Perplexity API: {e}")
        return None

def main():
    st.set_page_config(page_title="Resume Analyzer", page_icon="🤵", layout="wide")
    
    st.title("🤵 Resume/CV Analyzer")
    st.subheader("Optimize your resume for job applications")
    
    # API Key input (can be hidden in production by using .env or st.secrets)
    with st.expander("API Configuration"):
        api_key = st.text_input("Enter your Perplexity API Key", value=PERPLEXITY_API_KEY, type="password")
        if api_key:
            os.environ["PERPLEXITY_API_KEY"] = api_key
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.header("Job Description")
        job_description = st.text_area("Paste the job description here", height=300)
        
    with col2:
        st.header("Resume/CV")
        upload_option = st.radio("Choose an option:", ["Upload PDF", "Paste Text"])
        
        resume_text = ""
        if upload_option == "Upload PDF":
            uploaded_file = st.file_uploader("Upload your resume (PDF)", type="pdf")
            if uploaded_file:
                resume_text = extract_text_from_pdf(uploaded_file)
                with st.expander("View Extracted Text"):
                    st.text(resume_text)
        else:
            resume_text = st.text_area("Paste your resume text here", height=300)
    
    if st.button("Analyze Resume", type="primary") and job_description and resume_text:
        with st.spinner("Analyzing your resume against the job description..."):
            analysis = analyze_resume(resume_text, job_description)
            
            if analysis:
                st.success("Analysis complete!")
                st.markdown("## Analysis Results")
                st.markdown(analysis)
                
                # Add option to download the analysis
                st.download_button(
                    label="Download Analysis",
                    data=analysis,
                    file_name="resume_analysis.txt",
                    mime="text/plain"
                )
    
    # Instructions and about section
    with st.expander("How to use this tool"):
        st.markdown("""
        1. Enter your Perplexity API Key in the configuration section (get one from [Perplexity API](https://www.perplexity.ai/api))
        2. Paste the job description you're applying for
        3. Either upload your resume as a PDF or paste the text
        4. Click "Analyze Resume" to get personalized suggestions
        """)
    
    with st.expander("About"):
        st.markdown("""
        This Resume/CV Analyzer uses Perplexity's Sonar API to compare your resume against job descriptions.
        It provides suggestions to improve your resume, highlighting missing keywords and skills.
        
        Built for the Perplexity API Hackathon.
        """)

if __name__ == "__main__":
    main()
