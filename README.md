Resume Interview Bot
This is a Flask-based web application that uses the Google Generative AI API to conduct job interviews with candidates based on their resumes. The bot asks questions dynamically based on the candidate's answers and covers both work experience and soft skills. The interview is designed to last around 10-15 minutes, and the entire conversation, along with highlights and a rating, is sent to a specified email address after the interview.

**Features**


Dynamic, AI-driven interview process
Covers both work experience and soft skills
Redacts sensitive information from resumes
Sends the entire conversation, highlights, and rating to a specified email address

**Requirements**


Python 3.x
Flask
google-cloud-generativeai
PyPDF2

**Usage**

Upload your resume in PDF format.
Answer the bot's questions as they appear.
After the interview is complete, the conversation will be sent to the specified email address.
