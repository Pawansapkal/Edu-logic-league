from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func


BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / 'frontend'
DATABASE_PATH = Path(__file__).resolve().parent / 'database.sqlite'

app = Flask(
    __name__,
    static_folder=str(FRONTEND_DIR / 'assets'),
    static_url_path='/assets',
)
# Configure CORS for production deployment
cors_origins = [
    "http://localhost:5000",
    "http://localhost:3000",
    "http://127.0.0.1:5000",
    "https://pawansapkal.github.io",
    "*"  # Allow all origins as fallback
]
CORS(app, origins=cors_origins, supports_credentials=True)

app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DATABASE_PATH}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    xp = db.Column(db.Integer, default=0)
    level = db.Column(db.Integer, default=1)


class Challenge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(50), nullable=False)
    question_text = db.Column(db.String(200), nullable=False)
    options = db.Column(db.String(200), nullable=False)
    correct_answer = db.Column(db.String(50), nullable=False)
    xp_reward = db.Column(db.Integer, nullable=False)


class AnswerAttempt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    challenge_id = db.Column(db.Integer, db.ForeignKey('challenge.id'), nullable=False)
    is_correct = db.Column(db.Boolean, nullable=False)


def seed_data():
    if not User.query.filter_by(username='Student123').first():
        db.session.add(User(username='Student123', xp=100, level=2))

    if Challenge.query.count() == 0:
        db.session.add_all([
            Challenge(
                subject='Science',
                question_text='What is the SI unit of electric current?',
                options='Volt,Ampere,Ohm,Watt',
                correct_answer='Ampere',
                xp_reward=20,
            ),
            Challenge(
                subject='Math',
                question_text='What is the value of pi rounded to two decimal places?',
                options='3.12,3.14,3.16,3.18',
                correct_answer='3.14',
                xp_reward=15,
            ),
            Challenge(
                subject='History',
                question_text='Who was the first Prime Minister of independent India?',
                options='Mahatma Gandhi,Jawaharlal Nehru,Sardar Patel,Subhas Chandra Bose',
                correct_answer='Jawaharlal Nehru',
                xp_reward=15,
            ),
            Challenge(
                subject='English',
                question_text='Which part of speech is the word quickly?',
                options='Adjective,Adverb,Noun,Verb',
                correct_answer='Adverb',
                xp_reward=10,
            ),
        ])

    db.session.commit()


with app.app_context():
    db.create_all()
    seed_data()


def serialize_user(user):
    return {'username': user.username, 'xp': user.xp, 'level': user.level}


def get_or_create_user(username):
    sanitized_username = username.strip()
    user = User.query.filter_by(username=sanitized_username).first()
    if user:
        return user, False

    user = User(username=sanitized_username, xp=0, level=1)
    db.session.add(user)
    db.session.commit()
    return user, True


@app.get('/health')
def health_check():
    """Health check endpoint to prevent Render.com from sleeping"""
    return jsonify({'status': 'ok'}), 200


@app.get('/')
def serve_home():
    return send_from_directory(FRONTEND_DIR, 'index.html')


@app.get('/index.html')
def serve_index_page():
    return send_from_directory(FRONTEND_DIR, 'index.html')


@app.get('/arena.html')
def serve_arena_page():
    return send_from_directory(FRONTEND_DIR, 'arena.html')


@app.get('/dashboard.html')
def serve_dashboard_page():
    return send_from_directory(FRONTEND_DIR, 'dashboard.html')


@app.post('/api/user')
def create_user():
    data = request.get_json(silent=True) or {}
    username = (data.get('username') or '').strip()
    if not username:
        return jsonify({'error': 'Username is required.'}), 400

    user, created = get_or_create_user(username)
    response = serialize_user(user)
    response['created'] = created
    return jsonify(response), 201 if created else 200


@app.get('/api/user/<username>')
def get_user(username):
    user = User.query.filter_by(username=username.strip()).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404

    return jsonify(serialize_user(user))


@app.get('/api/challenge')
def get_challenge():
    challenge = Challenge.query.order_by(func.random()).first()
    if not challenge:
        return jsonify({'error': 'No challenges available'}), 404

    return jsonify({
        'id': challenge.id,
        'subject': challenge.subject,
        'question': challenge.question_text,
        'options': challenge.options.split(','),
        'xp_reward': challenge.xp_reward,
    })


@app.post('/api/submit')
def submit_answer():
    data = request.get_json(silent=True) or {}
    username = (data.get('username') or '').strip()
    challenge_id = data.get('challenge_id')
    answer = data.get('answer')

    if not username or challenge_id is None or answer is None:
        return jsonify({'error': 'username, challenge_id and answer are required'}), 400

    challenge = Challenge.query.get(challenge_id)
    user = User.query.filter_by(username=username).first()
    if not challenge or not user:
        return jsonify({'error': 'Invalid user or challenge'}), 404

    is_correct = answer == challenge.correct_answer
    db.session.add(AnswerAttempt(user_id=user.id, challenge_id=challenge.id, is_correct=is_correct))

    if is_correct:
        user.xp += challenge.xp_reward
        user.level = (user.xp // 100) + 1

    db.session.commit()

    if is_correct:
        return jsonify({
            'correct': True,
            'new_xp': user.xp,
            'new_level': user.level,
            'message': 'Correct! XP awarded.',
        })

    return jsonify({'correct': False, 'message': 'Incorrect. Try again!'})


@app.get('/api/dashboard/<username>')
def get_dashboard(username):
    user = User.query.filter_by(username=username.strip()).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404

    subjects = [row[0] for row in db.session.query(Challenge.subject).distinct().order_by(Challenge.subject).all()]
    mastery = []

    for subject in subjects:
        attempts = (
            db.session.query(AnswerAttempt.is_correct)
            .join(Challenge, Challenge.id == AnswerAttempt.challenge_id)
            .filter(AnswerAttempt.user_id == user.id, Challenge.subject == subject)
            .all()
        )
        total_attempts = len(attempts)
        correct_attempts = sum(1 for attempt in attempts if attempt.is_correct)
        score = round((correct_attempts / total_attempts) * 100) if total_attempts else 0
        mastery.append({'subject': subject, 'score': score})

    return jsonify({
        'username': user.username,
        'xp': user.xp,
        'level': user.level,
        'mastery': mastery,
    })


if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') != 'production'
    app.run(host='0.0.0.0', port=port, debug=debug)
