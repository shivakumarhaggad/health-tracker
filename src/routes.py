from flask import Blueprint, request, jsonify, render_template, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from .object_recognition import VisionAPI
from .models import db, User, HealthMetric
from .health_metrics import health_metric
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
routes = Blueprint('routes', __name__)
vision_api = VisionAPI()
api_key = os.getenv("OPENAI_API_KEY")


# Initialize OpenAI client
client = OpenAI(
    base_url="https://api.studio.nebius.ai/v1/",
    api_key=api_key
)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('routes.login'))
        return f(*args, **kwargs)
    return decorated_function

# Home route
@routes.route('/')
def index():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        return render_template('index.html', user=user)
    return render_template('index.html')

# User registration
@routes.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.form
        username = data.get('username')
        email = data.get('email')
        password = generate_password_hash(data.get('password'))

        if User.query.filter_by(email=email).first():
            return jsonify({"error": "Email already registered"}), 400

        if User.query.filter_by(username=username).first():
            return jsonify({"error": "Username already taken"}), 400

        new_user = User(username=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('routes.login'))
    return render_template('register.html')

# User login
@routes.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.form
        username = data.get('username')
        password = data.get('password')

        user = User.query.filter_by(username=username).first()
        if not user or not check_password_hash(user.password, password):
            return jsonify({"error": "Invalid username or password"}), 400

        session['user_id'] = user.id
        return redirect(url_for('routes.index'))

    return render_template('login.html')

# User logout
@routes.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('routes.index'))

# User profile
@routes.route("/profile")
@login_required
def profile():
    user = User.query.get(session['user_id']) 
    metrics = HealthMetric.query.filter_by(user_id=user.id).order_by(HealthMetric.timestamp.desc()).all()
    return render_template("profile.html", user=user, metrics=metrics)


# Image processing
@routes.route('/process', methods=['POST'])
@login_required
def process_image():
    try:
        image_url = None
        
        if 'file' in request.files:
            file = request.files['file']
            if file.filename != '':
                image_url = vision_api.upload_to_cloudinary(file)
                
        elif 'image_url' in request.form:
            image_url = request.form.get('image_url')
            
        if not image_url:
            return jsonify({"error": "No valid image provided"}), 400

        analysis_result = vision_api.analyze_image(image_url)
        
        return jsonify({
            "response": analysis_result,
            "image_url": image_url
        })

    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

@routes.route('/camera')
@login_required
def camera():
    return render_template('camera.html')

@routes.route('/settings')
@login_required
def settings():
    return render_template('settings.html')

@routes.route('/brainrot')
def brainrot():
    return render_template('brainrot.html')

# Register the health_metric blueprint
routes.register_blueprint(health_metric)

# Health Metrics
@routes.route('/health-metrics')
@login_required
def health_metrics():
    user = User.query.get(session['user_id'])
    return render_template('health-metrics.html', user=user)