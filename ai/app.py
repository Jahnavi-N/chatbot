# Save the following code in a file named app.py
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import openai

# Initialize Flask app and database
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chatbot.db'
db = SQLAlchemy(app)

# Initialize OpenAI
openai.api_key = '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'

# Define database models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    service = db.Column(db.String(100))
    action = db.Column(db.String(50))

@app.route('/submit', methods=['POST'])
def submit_user_details():
    data = request.json
    new_user = User(name=data['name'], email=data['email'], phone=data['phone'], service=data['service'], action=data['action'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User details saved successfully!"})

@app.route('/service-options', methods=['GET'])
def service_options():
    return jsonify({
        "options": [
            {"id": 1, "name": "Plumbing", "contact": "123-456-7890"},
            {"id": 2, "name": "Landscaping", "contact": "234-567-8901"},
            {"id": 3, "name": "Electrical", "contact": "345-678-9012"},
            {"id": 4, "name": "Roofing", "contact": "456-789-0123"}
        ]
    })

@app.route('/faq', methods=['GET'])
def get_faq():
    question = request.args.get('question')
    response = openai.Completion.create(
        model="gpt-4",
        prompt=f"Answer the following question based on the FAQ data: {question}",
        max_tokens=150
    )
    return jsonify({"answer": response.choices[0].text.strip()})

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
