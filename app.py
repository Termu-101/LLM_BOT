from flask import Flask, request, render_template, redirect, url_for, session
import google.generativeai as genai
from PyPDF2 import PdfReader
import re
import uuid

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Required for session handling

GOOGLE_API_KEY = "AIzaSyC7NlRz62EqH4FBJfvBE33kBns4ptN2uXk"
genai.configure(api_key=GOOGLE_API_KEY)

generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-pro",
    generation_config=generation_config,
    system_instruction="You are an interview bot that takes resumes from candidates and asks questions based on the resume. The questions must change dynamically with the candidates' answers. First, let the candidate insert their resume, then start asking questions. The questions must be of two types: one from the resume and another should be based on soft skills. The interview should last about 10-15 minutes, so manage the questions equally. Try to add questions from outside the resume depending on the work profile. After the interview is over, send the entire conversation, highlights of the interview, and a rating on these parameters [Hungry, solution-oriented, Focused] to terrmu10.10@gmail.com. Do not show these feedbacks to the candidate. Strict Instructions: Ask only one question at a time. Whenever a candidate ask any question to you just reply that you may ask me question after the interview and then at the ending of interview ask the candidate do you have any questions  "
)

chat_sessions = {}

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'resume' in request.files:
            uploaded_file = request.files['resume']
            try:
                reader = PdfReader(uploaded_file)
                resume_text = ""
                for page in reader.pages:
                    resume_text += page.extract_text()
                filtered_resume_text = filter_sensitive_info(resume_text)
                session['resume_content'] = filtered_resume_text
                session['uploaded_resume'] = True

                # Initialize the chat session and store its ID
                chat_session_id = str(uuid.uuid4())
                session['chat_session_id'] = chat_session_id
                chat_sessions[chat_session_id] = model.start_chat(history=[])

                response = chat_sessions[chat_session_id].send_message(filtered_resume_text)
                bot_question = response.text
                session['conversation_history'] = [{"role": "bot", "content": bot_question}]
                session['bot_question'] = bot_question

                return render_template('index.html', uploaded_resume=True, conversation_history=session['conversation_history'], bot_question=session['bot_question'])
            except Exception as e:
                return render_template('index.html', error=f"Error processing the PDF file: {e}")
        elif 'user_input' in request.form:
            user_input = request.form['user_input']
            session['conversation_history'].append({"role": "user", "content": user_input})

            chat_session_id = session['chat_session_id']
            response = chat_sessions[chat_session_id].send_message(user_input)
            bot_response = response.text

            session['conversation_history'].append({"role": "bot", "content": bot_response})
            session['bot_question'] = bot_response

            return render_template('index.html', uploaded_resume=True, conversation_history=session['conversation_history'])
    else:
        # Clear session data on page refresh and redirect to the upload resume page
        if 'uploaded_resume' in session and session['uploaded_resume']:
            session.clear()
            return redirect(url_for('index'))
        return render_template('index.html', uploaded_resume=False)

@app.route('/interview', methods=['GET'])
def interview():
    if 'uploaded_resume' in session and session['uploaded_resume']:
        return render_template('interview.html', conversation_history=session.get('conversation_history', []), bot_question=session.get('bot_question', ''))
    else:
        session.clear()
        return redirect(url_for('index'))

def filter_sensitive_info(text):
    patterns = [
        r'\b\d{10}\b',  # Matches phone numbers
        r'\b\w+@\w+\.\w+\b',  # Matches email addresses
        r'\bAddress\b.*',  # Matches lines starting with 'Address'
    ]
    for pattern in patterns:
        text = re.sub(pattern, '[REDACTED]', text, flags=re.IGNORECASE)
    return text

if __name__ == '__main__':
    app.run(debug=True)
