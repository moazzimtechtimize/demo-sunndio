from flask import Flask, render_template, request, jsonify, session
from markupsafe import Markup
import openai, re

app = Flask(__name__)
app.secret_key = 'supersecretkey'
# Set your OpenAI API key here
openai.api_key = 'sk-proj-JLjyOViY8wsGpBaLQ73BT3BlbkFJrB4ANPEUqXC8XJZKlBEv'

def llm(history):
    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are the world's most expert physiotherapist."},
                {"role": "user", "content": f"""
                    Ask some required question about the pain and then suggest a possible diagnosis and treatment to the user.
                    Make sure to Always ask questions one by one. Dont ask more than one things in one question.
                    Ask more and more questions to have more details about the user's pain.
                    Ask questions about every aspect of pain i.e. duration, type, category etc.
                    Be helpful. Explain the question, if user can't understand your question.
                    Keep diagnosis and treatments very short.
                    
                    Example:
                    \nDiagnosis:\n
                    These are the possible issues with you...  (Only tell Diagnosis names)
                    \nTreatment:\n
                    This treatment could be followed. (Only tell treatment names)
                    \nDuration:\n
                    It usually takes ------ weeks to cure.
                    \nFor Complete Treatment:\n
                    Visit https://sunndio.webflow.io/

                    Do not use any HTML tags, line breaks, or other formatting in your response.
                 
                    chat_history:{history}"""}
            ]
        )
        bot_response = response.choices[0].message.content
        
        return bot_response
    except openai.error.OpenAIError as e:
        return f"An error occurred: {str(e)}"


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start',methods=["POST","GET"])
def bot():
    session.clear()
    return render_template('bot.html')

@app.route("/ask", methods=["POST"])
def ask():
    user_input = request.form['msg']
    history = session.get('history', '')
    history += f"user: {user_input}\n"
    answer = llm(history)
    history += f"bot: {answer}\n"
    session['history'] = history
    
    # Markup to render HTML tags properly
    answer = re.sub(r'<br\s*/?>', '\n', answer)
    answer = Markup(answer)
    keywords = ["Diagnosis:", "Treatment:", "Duration:", "For Complete Treatment:"]
    pattern = r'(' + '|'.join(re.escape(word) for word in keywords) + r')'
    answer = re.sub(pattern, r'\n\1\n', answer)
    
    return jsonify({'answer': answer})

  
    


if __name__ == '__main__':
    app.run(debug=True)
