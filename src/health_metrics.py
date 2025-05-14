from flask import Blueprint, request, jsonify, session
from .models import db, HealthMetric
from functools import wraps
import openai
import os
from dotenv import load_dotenv
import random
import logging

load_dotenv()
health_metric = Blueprint('health_metric', __name__)

logging.basicConfig(level=logging.DEBUG)

# Set OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({"error": "Login required"}), 401
        return f(*args, **kwargs)
    return decorated_function

@health_metric.route('/api/health-metrics', methods=['POST'])
@login_required
def add_health_metric():
    try:
        data = request.json
        user_id = session['user_id']
        
        new_metric = HealthMetric(
            user_id=user_id,
            heart_rate=data.get('heart_rate'),
            blood_pressure_systolic=data.get('blood_pressure_systolic'),
            blood_pressure_diastolic=data.get('blood_pressure_diastolic'),
            calorie_count=data.get('calorie_count')
        )
        
        db.session.add(new_metric)
        db.session.commit()
        
        return jsonify({
            "message": "Health metric added successfully",
            "metric_id": new_metric.id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@health_metric.route('/api/health-metrics', methods=['GET'])
@login_required
def get_health_metrics():
    try:
        user_id = session['user_id']
        metrics = HealthMetric.query.filter_by(user_id=user_id).order_by(HealthMetric.timestamp.desc()).all()
        
        return jsonify({
            "metrics": [ {
                "id": metric.id,
                "heart_rate": metric.heart_rate,
                "blood_pressure_systolic": metric.blood_pressure_systolic,
                "blood_pressure_diastolic": metric.blood_pressure_diastolic,
                "calorie_count": metric.calorie_count,
                "timestamp": metric.timestamp.isoformat()
            } for metric in metrics]
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@health_metric.route('/api/health-tips', methods=['GET'])
@login_required
def get_health_tips():
    try:
        user_id = session['user_id']
        
        # Debugging: print the user_id to ensure it's being correctly retrieved
        logging.debug(f"User ID from session: {user_id}")

        # Query the latest health metric for the user
        latest_metric = HealthMetric.query.filter_by(user_id=user_id).order_by(HealthMetric.timestamp.desc()).first()
        
        # Debugging: print out the latest metric to see what is being fetched
        logging.debug(f"Latest health metric: {latest_metric}")

        if not latest_metric:
            logging.debug("No health metrics found for the user.")
            return jsonify({"message": "No health metrics found"}), 404

        # Determine health tips based on the user's health metrics
        health_tips = []

        # Heart Rate Tip
        if latest_metric.heart_rate < 60:
            health_tips.append("Your heart rate is on the lower end. Consider light exercises like walking to gradually increase your cardiovascular activity.")
        elif latest_metric.heart_rate > 100:
            health_tips.append("Your heart rate is elevated. Make sure to reduce stress and avoid strenuous activity. Consider checking with a healthcare provider.")
        else:
            health_tips.append("Your heart rate is in a healthy range. Keep up with regular exercise to maintain it!")

        # Blood Pressure Tip
        if latest_metric.blood_pressure_systolic < 120 and latest_metric.blood_pressure_diastolic < 80:
            health_tips.append("Your blood pressure is normal. Keep up the good work with a balanced diet and regular physical activity!")
        elif 120 <= latest_metric.blood_pressure_systolic < 130 and latest_metric.blood_pressure_diastolic < 80:
            health_tips.append("Your blood pressure is slightly elevated. Consider reducing your salt intake and maintaining a healthy weight.")
        elif 130 <= latest_metric.blood_pressure_systolic < 140 or 80 <= latest_metric.blood_pressure_diastolic < 90:
            health_tips.append("You may have stage 1 hypertension. Try to reduce stress, exercise regularly, and monitor your sodium intake.")
        elif latest_metric.blood_pressure_systolic >= 140 or latest_metric.blood_pressure_diastolic >= 90:
            health_tips.append("You may have stage 2 hypertension. Please consult with a healthcare professional to manage your blood pressure.")
        
        # Calorie Count Tip
        if latest_metric.calorie_count < 1000:
            health_tips.append("You're consuming too few calories. Consider including more nutrient-dense foods like fruits, vegetables, and whole grains.")
        elif latest_metric.calorie_count > 3000:
            health_tips.append("Your calorie intake is high. Try to adjust your diet to avoid excess weight gain, focusing on healthy foods like lean proteins and vegetables.")
        else:
            health_tips.append("Your calorie intake is within a healthy range. Keep balancing your diet with proper portions and nutritious foods.")

        return jsonify({
            "health_tips": random.choice(health_tips),
            "metrics": {
                "heart_rate": latest_metric.heart_rate,
                "blood_pressure": f"{latest_metric.blood_pressure_systolic}/{latest_metric.blood_pressure_diastolic}",
                "calorie_count": latest_metric.calorie_count
            }
        }), 200

    except Exception as e:
        # Log the exception
        logging.error(f"Exception occurred: {e}")
        return jsonify({
            "error": str(e),
            "fallback_tip": "Unable to retrieve health tips at the moment. Please maintain a healthy diet, stay active, and monitor your vital signs."
        }), 500


@health_metric.route('/api/health-metrics/<int:metric_id>', methods=['DELETE'])
@login_required
def delete_health_metric(metric_id):
    try:
        user_id = session['user_id']
        metric = HealthMetric.query.filter_by(id=metric_id, user_id=user_id).first()
        
        if not metric:
            return jsonify({"error": "Health metric not found"}), 404
        
        db.session.delete(metric)
        db.session.commit()
        
        return jsonify({"message": "Health metric deleted successfully"}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@health_metric.route('/api/health-metrics/<int:metric_id>', methods=['PUT'])
@login_required
def update_health_metric(metric_id):
    try:
        user_id = session['user_id']
        metric = HealthMetric.query.filter_by(id=metric_id, user_id=user_id).first()
        
        if not metric:
            return jsonify({"error": "Health metric not found"}), 404
        
        data = request.json
        metric.heart_rate = data.get('heart_rate', metric.heart_rate)
        metric.blood_pressure_systolic = data.get('blood_pressure_systolic', metric.blood_pressure_systolic)
        metric.blood_pressure_diastolic = data.get('blood_pressure_diastolic', metric.blood_pressure_diastolic)
        metric.calorie_count = data.get('calorie_count', metric.calorie_count)
        
        db.session.commit()
        
        return jsonify({"message": "Health metric updated successfully"}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@health_metric.route('/api/health-metrics/<int:metric_id>', methods=['GET'])
@login_required
def get_health_metric(metric_id):
    try:
        user_id = session['user_id']
        metric = HealthMetric.query.filter_by(id=metric_id, user_id=user_id).first()
        
        if not metric:
            return jsonify({"error": "Health metric not found"}), 404
        
        return jsonify({
            "id": metric.id,
            "heart_rate": metric.heart_rate,
            "blood_pressure_systolic": metric.blood_pressure_systolic,
            "blood_pressure_diastolic": metric.blood_pressure_diastolic,
            "calorie_count": metric.calorie_count,
            "timestamp": metric.timestamp.isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@health_metric.route('/api/health-metrics/summary', methods=['GET'])
@login_required
def get_health_metrics_summary():
    try:
        user_id = session['user_id']
        metrics = HealthMetric.query.filter_by(user_id=user_id).all()
        
        if not metrics:
            return jsonify({"message": "No health metrics found"}), 404
        
        heart_rate_avg = sum([metric.heart_rate for metric in metrics]) / len(metrics)
        bp_systolic_avg = sum([metric.blood_pressure_systolic for metric in metrics]) / len(metrics)
        bp_diastolic_avg = sum([metric.blood_pressure_diastolic for metric in metrics]) / len(metrics)
        calorie_count_avg = sum([metric.calorie_count for metric in metrics]) / len(metrics)
        
        return jsonify({
            "heart_rate_avg": heart_rate_avg,
            "blood_pressure_systolic_avg": bp_systolic_avg,
            "blood_pressure_diastolic_avg": bp_diastolic_avg,
            "calorie_count_avg": calorie_count_avg
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@health_metric.route('/api/health-metrics/summary', methods=['DELETE'])
@login_required
def delete_health_metrics():
    try:
        user_id = session['user_id']
        metrics = HealthMetric.query.filter_by(user_id=user_id).all()
        
        if not metrics:
            return jsonify({"message": "No health metrics found"}), 404
        
        for metric in metrics:
            db.session.delete(metric)
        
        db.session.commit()
        
        return jsonify({"message": "All health metrics deleted successfully"}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
