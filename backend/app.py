from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
# Allow the frontend (HTML/JS) to communicate with this backend
CORS(app)

# Setup a simple SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- MODELS (Normally in backend/models/ users.py & challenges.py) ---
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    xp = db.Column(db.Integer, default=0)
    level = db.Column(db.Integer, default=1)

class Challenge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(50))
    question_text = db.Column(db.String(200))
    options = db.Column(db.String(200)) # Stored as comma-separated
    correct_answer = db.Column(db.String(50))
    xp_reward = db.Column(db.Integer)

# Create tables and add dummy data if empty
with app.app_context():
    db.create_all()
    if not User.query.first():
        db.session.add(User(username="Student123", xp=100, level=2))
        db.session.add(Challenge(
            subject="Science", 
            question_text="What is the SI unit of electric current?", 
            options="Volt,Ampere,Ohm,Watt", 
            correct_answer="Ampere", 
            xp_reward=20
        ))
        db.session.commit()

# --- ROUTES (Normally in backend/routes/ game_routes.py) ---
@app.route('/api/user/<username>', methods=['GET'])
def get_user(username):
    user = User.query.filter_by(username=username).first()
    if user:
        return jsonify({"username": user.username, "xp": user.xp, "level": user.level})
    return jsonify({"error": "User not found"}), 404

@app.route('/api/challenge', methods=['GET'])
def get_challenge():
    # For MVP, just grab the first challenge
    challenge = Challenge.query.first()
    return jsonify({
        "id": challenge.id,
        "subject": challenge.subject,
        "question": challenge.question_text,
        "options": challenge.options.split(','),
        "xp_reward": challenge.xp_reward
    })

@app.route('/api/submit', methods=['POST'])
def submit_answer():
    data = request.json
    challenge = Challenge.query.get(data['challenge_id'])
    user = User.query.filter_by(username=data['username']).first()
    
    if data['answer'] == challenge.correct_answer:
        user.xp += challenge.xp_reward
        # Simple level up logic: Level up every 100 XP
        user.level = (user.xp // 100) + 1 
        db.session.commit()
        return jsonify({"correct": True, "new_xp": user.xp, "new_level": user.level, "message": "Correct! XP Awarded."})
    
    return jsonify({"correct": False, "message": "Incorrect. Try again!"})

if __name__ == '__main__':
    app.run(debug=True)
