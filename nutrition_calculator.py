def parse_units(value_str):
    """Parse height/weight strings with units into metric values"""
    if not value_str:
        return 0.0
    value_str = value_str.lower().strip()
    if 'cm' in value_str:
        return float(value_str.replace('cm', '').strip())
    elif 'kg' in value_str:
        return float(value_str.replace('kg', '').strip())
    elif 'lbs' in value_str:
        lbs = float(value_str.replace('lbs', '').strip())
        return lbs * 0.453592
    elif 'ft' in value_str and 'in' in value_str:
        parts = value_str.split('ft')
        ft_part = float(parts[0].strip())
        in_part = float(parts[1].replace('in', '').strip()) if len(parts) > 1 else 0
        return ft_part * 30.48 + in_part * 2.54
    try:
        return float(value_str)
    except:
        return 0.0

def calculate_bmr(weight_kg, height_cm, age, gender):
    """Calculate BMR using Mifflin-St Jeor equation"""
    if gender.lower() == 'male':
        return 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
    else:  # Female or other
        return 10 * weight_kg + 6.25 * height_cm - 5 * age - 161

def calculate_tdee(bmr, activity_level):
    """Calculate TDEE based on activity level"""
    activity_factors = {
        'sedentary': 1.2,
        'lightly active': 1.375,
        'moderately active': 1.55,
        'very active': 1.725,
        'extremely active': 1.9
    }
    return bmr * activity_factors.get(activity_level.lower(), 1.2)

def build_restriction_profile(conditions):
    """Create detailed nutrition rules and food recommendations"""
    rules = {
        'max_sodium_mg': None,
        'max_simple_carbs_g': None,
        'min_fiber_g': None,
        'max_protein_g_per_kg': None,
        'max_potassium_mg': None,
        'avoid_ingredients': [],
        'preferred_ingredients': [],
        'what_to_eat': [],
        'what_to_avoid': []
    }
    
    if 'diabetes' in conditions:
        rules['max_simple_carbs_g'] = 50
        rules['min_fiber_g'] = 30
        rules['avoid_ingredients'].extend(['sugar', 'white bread', 'soda', 'candy'])
        rules['preferred_ingredients'].extend(['whole grains', 'vegetables', 'legumes'])
        rules['what_to_eat'].extend(['Non-starchy vegetables', 'Whole grains', 'Lean proteins'])
        rules['what_to_avoid'].extend(['Sugary drinks', 'Processed snacks', 'White rice'])
    
    if 'hypertension' in conditions:
        rules['max_sodium_mg'] = 2300
        rules['avoid_ingredients'].extend(['salt', 'processed meats', 'pickles'])
        rules['preferred_ingredients'].extend(['fruits', 'vegetables', 'low-fat dairy'])
        rules['what_to_eat'].extend(['Leafy greens', 'Berries', 'Oats'])
        rules['what_to_avoid'].extend(['Canned soups', 'Frozen pizzas', 'Soy sauce'])
    
    if 'chronic kidney disease' in conditions:
        rules['max_protein_g_per_kg'] = 0.8
        rules['max_potassium_mg'] = 2000
        rules['avoid_ingredients'].extend(['bananas', 'potatoes', 'tomatoes'])
        rules['preferred_ingredients'].extend(['egg whites', 'cauliflower', 'apples'])
        rules['what_to_eat'].extend(['Cauliflower rice', 'Blueberries', 'Skinless chicken'])
        rules['what_to_avoid'].extend(['Avocados', 'Spinach', 'Oranges'])
    
    if 'pcos' in conditions:
        rules['avoid_ingredients'].extend(['refined carbs', 'sugary drinks'])
        rules['preferred_ingredients'].extend(['high fiber foods', 'lean proteins'])
        rules['what_to_eat'].extend(['Broccoli', 'Salmon', 'Chia seeds'])
        rules['what_to_avoid'].extend(['Sugary cereals', 'Fried foods', 'White pasta'])
    
    if 'ibs' in conditions:
        rules['avoid_ingredients'].extend(['caffeine', 'alcohol', 'fatty foods'])
        rules['preferred_ingredients'].extend(['low FODMAP foods', 'probiotics'])
        rules['what_to_eat'].extend(['Ginger tea', 'Oatmeal', 'Cucumber'])
        rules['what_to_avoid'].extend(['Garlic', 'Onions', 'Beans'])
    
    # Remove None values and empty lists
    return {k: v for k, v in rules.items() if v not in [None, [], '']}

def build_ingredient_compatibility(preferences):
    """Generate allowed ingredients with more detailed database"""
    ingredient_db = {
        'Tofu': {'diet': ['vegan', 'vegetarian'], 'allergens': []},
        'Lentils': {'diet': ['vegan', 'vegetarian'], 'allergens': []},
        'Quinoa': {'diet': ['vegan', 'vegetarian', 'gluten-free'], 'allergens': []},
        'Vegetables': {'diet': ['all'], 'allergens': []},
        'Avocado': {'diet': ['vegan', 'vegetarian'], 'allergens': []},
        'Eggs': {'diet': ['vegetarian'], 'allergens': ['eggs']},
        'Cheese': {'diet': ['vegetarian'], 'allergens': ['dairy']},
        'Chicken': {'diet': ['omnivore'], 'allergens': []},
        'Salmon': {'diet': ['omnivore'], 'allergens': ['seafood']},
        'Almonds': {'diet': ['all'], 'allergens': ['nuts']},
        'Walnuts': {'diet': ['all'], 'allergens': ['nuts']},
        'Milk': {'diet': ['vegetarian'], 'allergens': ['dairy']},
        'Whole wheat bread': {'diet': ['vegetarian', 'vegan'], 'allergens': ['gluten']},
        'Brown rice': {'diet': ['all'], 'allergens': []}
    }

    compatible = []
    diet_type = preferences.get('diet_type', '').lower()
    allergies = [a.lower() for a in preferences.get('allergies', [])]
    
    for ingredient, props in ingredient_db.items():
        # Check diet compatibility
        diet_ok = diet_type in props['diet'] or 'all' in props['diet']
        
        # Check allergy compatibility
        allergy_ok = not any(allergen in props['allergens'] for allergen in allergies)
        
        if diet_ok and allergy_ok:
            compatible.append(ingredient)
    
    return compatible

def calculate_goals(tdee, goal, current_weight, goal_weight, timeline_weeks):
    """Calculate detailed nutritional targets"""
    if timeline_weeks <= 0:
        timeline_weeks = 1
    
    weight_diff = goal_weight - current_weight
    daily_calorie_adjust = (weight_diff * 7700) / (timeline_weeks * 7)
    
    # Apply safe limits
    if goal == 'weight loss':
        daily_calorie_adjust = max(min(daily_calorie_adjust, -500), -700)
        protein_ratio = 0.35
        carb_ratio = 0.40
        fat_ratio = 0.25
        fiber_g = 35
    elif goal == 'muscle gain':
        daily_calorie_adjust = min(max(daily_calorie_adjust, 300), 500)
        protein_ratio = 0.30
        carb_ratio = 0.45
        fat_ratio = 0.25
        fiber_g = 30
    else:  # Maintenance
        daily_calorie_adjust = 0
        protein_ratio = 0.25
        carb_ratio = 0.50
        fat_ratio = 0.25
        fiber_g = 28
    
    target_calories = tdee + daily_calorie_adjust
    
    return {
        'calories': round(target_calories, 2),
        'protein_g': round((target_calories * protein_ratio) / 4, 2),
        'carbs_g': round((target_calories * carb_ratio) / 4, 2),
        'fat_g': round((target_calories * fat_ratio) / 9, 2),
        'fiber_g': fiber_g,
        'water_ml': round(current_weight * 30, 2)  # 30ml per kg of body weight
    }
