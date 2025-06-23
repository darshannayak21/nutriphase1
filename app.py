from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from nutrition_calculator import *

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/calculate_profile', methods=['POST'])
def calculate_profile():
    data = request.json
    
    try:
        # Parse units
        weight_kg = parse_units(data['weight'])
        height_cm = parse_units(data['height'])
        
        # 1.1 Core Profile
        bmr = calculate_bmr(weight_kg, height_cm, data['age'], data['gender'])
        tdee = calculate_tdee(bmr, data['activity_level'])
        
        # 1.2 Health Profile
        restriction_profile = build_restriction_profile(data.get('medical_conditions', []))
        
        # 1.3 Dietary Preferences
        ingredient_list = build_ingredient_compatibility({
            'diet_type': data['diet_type'],
            'allergies': data.get('allergies', [])
        })
        
        # 1.4 Goal Setting
        goal_weight = parse_units(data['goal_weight'])
        nutrition_targets = calculate_goals(
            tdee,
            data['main_health_goal'],
            weight_kg,
            goal_weight,
            data['goal_timeline_weeks']
        )
        
        return jsonify({
            'bmr': round(bmr, 2),
            'tdee': round(tdee, 2),
            'restriction_profile': restriction_profile,
            'ingredient_compatibility_list': ingredient_list,
            'daily_nutrition_targets': nutrition_targets
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(port=5000, debug=True)
